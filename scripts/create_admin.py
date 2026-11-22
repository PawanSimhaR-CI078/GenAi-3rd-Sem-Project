"""Create an admin account. Usage: python scripts/create_admin.py <username> <password> [ADMIN|SUPER_ADMIN]"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app
from app.models.user import create_user, get_user_by_username

app = create_app()
with app.app_context():
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_admin.py <username> <password> [ADMIN|SUPER_ADMIN]")
        sys.exit(1)
    uname, pw = sys.argv[1], sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "ADMIN"
    if get_user_by_username(uname):
        print("User already exists")
        sys.exit(1)
    uid = create_user(uname, pw, display_name=uname, role=role, created_by=None)
    print(f"Created {role} user '{uname}' (id={uid})")