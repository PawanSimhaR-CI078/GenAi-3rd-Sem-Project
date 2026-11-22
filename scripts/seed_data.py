"""Seed TOLSTOY with dummy data. Usage: python scripts/seed_data.py"""
import os, sys, random, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app
from app.db import get_db, close_db
from app.models.user import create_user
from app.models.story import create_story, update_story
from app.models.system_settings import set_setting
from app.services.bootstrap import bootstrap
from datetime import datetime, timezone

random.seed(42)

app = create_app("development")
with app.app_context():
    # reset tables
    db = get_db()
    db.execute("DELETE FROM tolstoy_stories")
    db.execute("DELETE FROM tolstoy_users")
    db.execute("DELETE FROM tolstoy_system_settings")
    db.commit()

    bootstrap()

    # admins
    create_user("Pawan Simha R", "iamadmin", display_name="Pawan Simha R", role="SUPER_ADMIN", created_by=None)
    create_user("Bajarangi", "iamadmin", display_name="Bajarangi", role="ADMIN", created_by=None)

    first = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Ayaan","Krishna","Ishaan","Shaurya","Atharv","Advik","Pranav","Rudra","Kabir","Shivansh","Dhruv","Ritvik","Kian","Ananya","Diya","Saanvi","Aadhya","Pari","Anika","Navya","Myra","Aanya","Riya","Avni","Ira","Sara","Tara","Zara","Meera","Nisha","Priya","Kavya","Ishita","Rohan","Rahul","Amit","Vikram","Suresh","Raj","Karan","Neha","Pooja","Sneha"]
    last = ["Sharma","Verma","Patel","Singh","Kumar","Gupta","Joshi","Mehta","Reddy","Nair","Iyer","Rao","Das","Bose","Khan","Ali","Chopra","Malhotra","Kapoor","Agarwal"]

    sample_script = {
        "title": "Sample",
        "scenes": [
            {"scene_number": 1, "setting": "A quiet village at dawn",
             "panels": [
                {"panel_number": 1, "description": "Hero looks at the horizon", "characters": ["Hero"],
                 "dialogue": [{"character": "Hero", "line": "Today is the day."}], "narration": "The sun rises."},
                {"panel_number": 2, "description": "Villagers gather", "characters": ["Villager"],
                 "dialogue": [{"character": "Villager", "line": "Is it true?"}], "narration": "Whispers spread."}
             ]}
        ]
    }

    genres = ["children", "teens", "adults", "all ages"]
    lengths = ["short", "medium", "long"]
    langs = ["English", "Hindi", "Spanish"]
    genders = ["male", "female", "non-binary", None]

    for i in range(50):
        uname = f"{random.choice(first).lower()}{random.choice(last).lower()}{i+1}"
        create_user(uname, "iamuser", display_name=f"{random.choice(first)} {random.choice(last)}",
                    phone_number=f"+91{random.randint(7000000000,9999999999)}", role="USER", created_by=None)

    users = db.execute("SELECT id, username FROM tolstoy_users WHERE role='USER'").fetchall()

    story_titles = ["The Last Warrior", "Moonlit Forest", "City of Dreams", "The Hidden Key",
                    "Journey Home", "Shadows of Past", "The Brave Little Robot", "Ocean's Secret",
                    "Fire and Ice", "The Magic Book", "Lost in Time", "The Golden Crown"]

    for u in users:
        n_stories = random.randint(1, 4)
        for _ in range(n_stories):
            sid = create_story(
                u["id"], random.choice(story_titles),
                "Once upon a time in a land far away, there lived a brave soul who embarked on an unforgettable journey.",
                character_gender=random.choice(genders),
                target_audience=random.choice(genres),
                desired_length=random.choice(lengths),
                language=random.choice(langs),
                created_by=u["id"],
            )
            # randomly mark completed / generated
            if random.random() < 0.4:
                update_story(sid, {"story_status": "COMPLETED"}, u["id"])
            if random.random() < 0.6:
                update_story(sid, {
                    "generated_script": json.dumps(sample_script),
                    "generation_status": "succeeded",
                    "tokens_consumed": random.choice([1, 2]),
                    "gemini_input_tokens": random.randint(100, 500),
                    "gemini_output_tokens": random.randint(200, 800),
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }, u["id"])
            elif random.random() < 0.2:
                update_story(sid, {"generation_status": "failed"}, u["id"])

    # adjust token balances randomly
    for u in users:
        bal = random.choice([0, 1, 2, 3, 5, 7, 10])
        db.execute("UPDATE tolstoy_users SET token_balance=? WHERE id=?", (bal, u["id"]))
    db.commit()

    print("Users:", db.execute("SELECT COUNT(*) FROM tolstoy_users").fetchone()[0])
    print("Stories:", db.execute("SELECT COUNT(*) FROM tolstoy_stories").fetchone()[0])
    print("Admins:", db.execute("SELECT username, role FROM tolstoy_users WHERE role IN ('ADMIN','SUPER_ADMIN')").fetchall())