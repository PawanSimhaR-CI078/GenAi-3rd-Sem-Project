"""System Integration Test (SIT) — end-to-end API validation against a running server."""
import sys, uuid, json
import requests

BASE = "http://127.0.0.1:5001"
results = []

def rec(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("PASS" if ok else "FAIL"), "-", name, ("| " + str(detail) if detail else ""))

def session():
    s = requests.Session()
    r = s.get(BASE + "/api/v1/auth/csrf")
    tok = r.json()["data"]["csrf_token"]
    s.headers.update({"X-CSRFToken": tok, "Content-Type": "application/json"})
    return s

def jget(r):
    try: return r.json()
    except Exception: return {}

# --- public pages ---
for p in ["/", "/login", "/register", "/admin/login", "/maintenance"]:
    r = requests.get(BASE + p)
    rec(f"GET {p} 200", r.status_code == 200, r.status_code)

r = requests.get(BASE + "/dashboard", allow_redirects=False)
rec("GET /dashboard unauth redirects", r.status_code in (302, 303), r.status_code)

# --- registration ---
u = "situser" + uuid.uuid4().hex[:8]
s = session()
r = s.post(BASE + "/api/v1/auth/register", json={"username": u, "password": "password123", "display_name": "SIT User"})
rec("POST register 201", r.status_code == 201, r.text[:120])

r = s.post(BASE + "/api/v1/auth/register", json={"username": u, "password": "password123"})
rec("POST duplicate register 409", r.status_code == 409, r.status_code)

r = s.post(BASE + "/api/v1/auth/register", json={"username": "ab", "password": "short"})
rec("POST invalid register 400", r.status_code == 400, r.status_code)

# --- login ---
r = s.post(BASE + "/api/v1/auth/user/login", json={"username": u, "password": "password123"})
rec("POST user login 200", r.status_code == 200, r.text[:100])

r = s.get(BASE + "/home")
rec("GET /home after user login 200", r.status_code == 200 and "Welcome back" in r.text, r.status_code)

r = s.post(BASE + "/api/v1/auth/user/login", json={"username": u, "password": "wrongpass"})
rec("POST bad password 401", r.status_code == 401, r.status_code)

r = s.get(BASE + "/api/v1/auth/me")
me = jget(r)
rec("GET me 200", r.status_code == 200 and me.get("data", {}).get("username") == u, r.status_code)

# --- wallet ---
r = s.get(BASE + "/api/v1/wallet")
w = jget(r).get("data", {})
rec("Wallet initial balance 5", r.status_code == 200 and w.get("token_balance") == 5, w)

# --- story lifecycle ---
r = s.post(BASE + "/api/v1/stories", json={"title": "SIT Story", "content": "A test story about a brave cat.", "target_audience": "children", "desired_length": "short", "language": "English"})
sid = jget(r).get("data", {}).get("story_id")
rec("POST story 201", r.status_code == 201 and sid, r.text[:100])

r = s.get(BASE + "/api/v1/stories")
rec("GET stories list", r.status_code == 200 and any(x["id"] == sid for x in jget(r)["data"]["stories"]), r.status_code)

r = s.get(f"{BASE}/api/v1/stories/{sid}")
rec("GET story detail", r.status_code == 200, r.status_code)

r = s.patch(f"{BASE}/api/v1/stories/{sid}", json={"title": "SIT Story Updated"})
rec("PATCH story", r.status_code == 200, r.status_code)

r = s.patch(f"{BASE}/api/v1/stories/{sid}/status", json={"story_status": "COMPLETED"})
rec("PATCH status COMPLETED", r.status_code == 200, r.status_code)
r = s.get(f"{BASE}/api/v1/stories/{sid}")
rec("Verify status persisted", jget(r)["data"]["story"]["story_status"] == "COMPLETED")

r = s.patch(f"{BASE}/api/v1/stories/{sid}/status", json={"story_status": "BOGUS"})
rec("PATCH invalid status 400", r.status_code == 400, r.status_code)

# --- generation without Gemini key: should fail AND refund ---
r = s.post(f"{BASE}/api/v1/stories/{sid}/generate")
gj = jget(r)
rec("Generate without key returns error", r.status_code in (502, 504, 429) or not gj.get("success"), r.status_code)
r = s.get(BASE + "/api/v1/wallet")
rec("Tokens refunded after failed generation", jget(r)["data"]["token_balance"] == 5, jget(r)["data"])

# --- ownership ---
s2 = session()
u2 = "situser" + uuid.uuid4().hex[:8]
s2.post(BASE + "/api/v1/auth/register", json={"username": u2, "password": "password123"})
s2.post(BASE + "/api/v1/auth/user/login", json={"username": u2, "password": "password123"})
r = s2.get(f"{BASE}/api/v1/stories/{sid}")
rec("Cross-user story access 403", r.status_code == 403, r.status_code)
r = s2.patch(f"{BASE}/api/v1/stories/{sid}/status", json={"story_status": "EDITING"})
rec("Cross-user status change 403", r.status_code == 403, r.status_code)
r = s2.delete(f"{BASE}/api/v1/stories/{sid}")
rec("Cross-user delete 403", r.status_code == 403, r.status_code)

# --- contact (mail not configured) ---
r = s.post(BASE + "/api/v1/contact", json={"subject": "Help", "message": "Need tokens"})
rec("Contact returns controlled error", r.status_code in (200, 500), r.text[:80])

# --- admin ---
a = session()
r = a.post(BASE + "/api/v1/auth/admin/login", json={"username": "Pawan Simha R", "password": "iamsuperadmin"})
rec("Admin login 200", r.status_code == 200, r.text[:100])

r = a.get(BASE + "/admin/home")
rec("GET /admin/home after admin login 200", r.status_code == 200 and "Welcome back" in r.text, r.status_code)

r = a.get(BASE + "/admin")
rec("GET /admin KPI tones 200", r.status_code == 200 and "card('Generation success'" in r.text and "'good'" in r.text and "'bad'" in r.text and "GEMINI_MARK" in r.text and "borderSkipped: 'bottom'" in r.text, r.status_code)

r = a.get(BASE + "/api/v1/admin/users")
rec("Admin users list", r.status_code == 200 and len(jget(r)["data"]["users"]) > 0, r.status_code)
uid = jget(a.get(BASE + "/api/v1/admin/users"))["data"]["users"][0]["id"]
r = a.get(BASE + f"/api/v1/admin/users/{uid}")
rec("Admin user detail no hash", r.status_code == 200 and "password_hash" not in jget(r)["data"]["user"], r.status_code)

r = a.get(BASE + "/api/v1/admin/stories")
rec("Admin stories list", r.status_code == 200, r.status_code)
r = a.get(BASE + "/api/v1/admin/analytics/summary")
rec("Analytics summary", r.status_code == 200 and "users" in jget(r)["data"], r.status_code)
r = a.get(BASE + "/api/v1/admin/analytics/db-health")
rec("Analytics DB health", r.status_code == 200 and "tables" in jget(r)["data"], r.status_code)
for key in ["users_growth", "users_role", "stories_status", "generation_status", "stories_per_day", "tokens_per_day", "gemini_usage", "top_users", "story_mix"]:
    r = a.get(BASE + "/api/v1/admin/analytics/charts", params={"chart": key})
    rec(f"Chart data {key}", r.status_code == 200 and "labels" in jget(r)["data"], r.status_code)
r = a.get(BASE + "/api/v1/admin/database/tolstoy_users")
rows = jget(r).get("data", {}).get("rows", [])
rec("DB viewer hides hashes", r.status_code == 200 and all("password_hash" not in x for x in rows), r.status_code)
r = a.get(BASE + "/api/v1/admin/database/nope")
rec("DB viewer rejects unknown table", r.status_code == 400, r.status_code)
r = a.get(BASE + "/api/v1/admin/roles/permissions")
rec("Role permissions list", r.status_code == 200 and "capabilities" in jget(r)["data"], r.status_code)
r = a.get(BASE + "/api/v1/admin/system/status")
rec("System status", r.status_code == 200 and "enabled" in jget(r)["data"], r.status_code)
r = a.get(BASE + "/api/v1/admin/settings")
rec("Admin settings list", r.status_code == 200, r.status_code)
r = a.patch(BASE + f"/api/v1/admin/users/{uid}/tokens", json={"increase": 1})
rec("Token increase allowed", r.status_code == 200, r.status_code)
r = a.patch(BASE + f"/api/v1/admin/users/{uid}/tokens", json={"adjustment": -1})
rec("Token decrease rejected", r.status_code == 400, r.status_code)

# --- role separation ---
adm = session()
r = adm.post(BASE + "/api/v1/auth/admin/login", json={"username": "Ramesh", "password": "iamadmin"})
rec("Admin login 200", r.status_code == 200, r.status_code)
for path in ["/admin", "/admin/users", "/admin/database", "/admin/stories"]:
    rec(f"Admin allowed {path}", adm.get(BASE + path).status_code == 200, path)
for path in ["/admin/roles", "/admin/system", "/admin/settings"]:
    rec(f"Admin blocked {path}", adm.get(BASE + path).status_code == 403, path)
rec("Admin blocked wallet edit", adm.patch(BASE + f"/api/v1/admin/users/{uid}/tokens", json={"increase": 1}).status_code == 403)
rec("Admin blocked offline toggle", adm.patch(BASE + "/api/v1/admin/maintenance", json={"enabled": True, "password": "iamadmin"}).status_code == 403)

# --- maintenance ---
r = a.patch(BASE + "/api/v1/admin/maintenance", json={"enabled": True, "password": "wrong"})
rec("Maintenance wrong password 401", r.status_code == 401, r.status_code)
r = a.patch(BASE + "/api/v1/admin/maintenance", json={"enabled": True, "password": "iamsuperadmin"})
rec("Maintenance enable 200", r.status_code == 200, r.status_code)
r = s.get(BASE + "/api/v1/stories")
rec("User blocked in maintenance 503", r.status_code == 503, r.status_code)
r = a.get(BASE + "/api/v1/admin/users")
rec("Admin allowed in maintenance", r.status_code == 200, r.status_code)
r = a.get(BASE + "/home", allow_redirects=False)
rec("Admin welcome reachable in maintenance", r.status_code == 302 and "/admin/home" in r.headers.get("Location", ""), r.status_code)
r = a.patch(BASE + "/api/v1/admin/maintenance", json={"enabled": False, "password": "iamsuperadmin"})
rec("Maintenance disable 200", r.status_code == 200, r.status_code)

# --- user cannot access admin endpoints / pages ---
r = s.get(BASE + "/api/v1/admin/users")
rec("User blocked from admin API 403", r.status_code == 403, r.status_code)
r = s.get(BASE + "/admin", allow_redirects=False)
rec("User blocked from admin page", r.status_code == 403, r.status_code)

# --- delete story ---
r = s.delete(f"{BASE}/api/v1/stories/{sid}")
rec("DELETE story 200", r.status_code == 200, r.status_code)
r = s.get(f"{BASE}/api/v1/stories/{sid}")
rec("Deleted story 404", r.status_code == 404, r.status_code)

# --- logout ---
r = s.post(BASE + "/api/v1/auth/logout")
rec("Logout 200", r.status_code == 200, r.status_code)
r = s.get(BASE + "/api/v1/auth/me")
rec("Me after logout 401", r.status_code == 401, r.status_code)

# --- CSRF enforcement ---
plain = requests.Session()
r = plain.post(BASE + "/api/v1/auth/user/login", json={"username": u, "password": "password123"})
rec("Login without CSRF rejected 400", r.status_code == 400, r.status_code)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print("\n==== SIT RESULT:", passed, "/", total, "passed ====")
sys.exit(0 if passed == total else 1)