"""Seed TOLSTOY with a clean demo dataset. Usage: python scripts/seed_data.py"""
import json
import os
import random
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.db import get_db
from app.models.story import create_story, update_story
from app.services.bootstrap import bootstrap

random.seed(42)
USER_COUNT = 55

first = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
         "Krishna", "Ishaan", "Shaurya", "Atharv", "Advik", "Pranav", "Rudra", "Kabir",
         "Ananya", "Diya", "Saanvi", "Aadhya", "Pari", "Anika", "Navya", "Myra", "Aanya",
         "Riya", "Avni", "Ira", "Sara", "Tara", "Zara", "Meera", "Nisha", "Priya", "Kavya",
         "Rohan", "Rahul", "Amit", "Vikram", "Raj", "Karan", "Neha", "Pooja", "Sneha"]
last = ["Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Joshi", "Mehta",
        "Reddy", "Nair", "Iyer", "Rao", "Das", "Bose", "Khan", "Ali", "Chopra",
        "Malhotra", "Kapoor", "Agarwal"]

story_titles = ["The Last Warrior", "Moonlit Forest", "City of Dreams", "The Hidden Key",
                "Journey Home", "Shadows of Past", "The Brave Little Robot", "Ocean's Secret",
                "Fire and Ice", "The Magic Book", "Lost in Time", "The Golden Crown"]
genres = ["children", "teens", "adults", "all ages"]
lengths = ["short", "medium", "long"]
langs = ["English", "Hindi", "Spanish"]
genders = ["male", "female", "non-binary", None]

sample_script = {
    "title": "Sample",
    "scenes": [{
        "scene_number": 1,
        "setting": "A quiet village at dawn",
        "panels": [
            {"panel_number": 1, "description": "Hero looks at the horizon",
             "characters": ["Hero"],
             "dialogue": [{"character": "Hero", "line": "Today is the day."}],
             "narration": "The sun rises."},
            {"panel_number": 2, "description": "Villagers gather",
             "characters": ["Villager"],
             "dialogue": [{"character": "Villager", "line": "Is it true?"}],
             "narration": "Whispers spread."},
        ],
    }],
}


def seed_users(db):
    from app.models.user import create_user
    for i in range(USER_COUNT):
        uname = f"{random.choice(first).lower()}{random.choice(last).lower()}{i + 1}"
        create_user(
            uname, "iamuser",
            display_name=f"{random.choice(first)} {random.choice(last)}",
            phone_number=f"+91{random.randint(7000000000, 9999999999)}",
            role="USER", created_by=None,
        )
    return db.execute("SELECT id FROM tolstoy_users WHERE role='USER'").fetchall()


def seed_stories(db, users):
    for u in users:
        for _ in range(random.randint(1, 4)):
            sid = create_story(
                u["id"], random.choice(story_titles),
                "Once upon a time in a land far away, there lived a brave soul who embarked on an unforgettable journey.",
                character_gender=random.choice(genders),
                target_audience=random.choice(genres),
                desired_length=random.choice(lengths),
                language=random.choice(langs),
                created_by=u["id"],
            )
            if random.random() < 0.4:
                update_story(sid, {"story_status": "COMPLETED"}, u["id"])
            roll = random.random()
            if roll < 0.6:
                update_story(sid, {
                    "generated_script": json.dumps(sample_script),
                    "generation_status": "succeeded",
                    "tokens_consumed": random.choice([1, 2]),
                    "gemini_input_tokens": random.randint(100, 500),
                    "gemini_output_tokens": random.randint(200, 800),
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }, u["id"])
            elif roll < 0.8:
                update_story(sid, {"generation_status": "failed"}, u["id"])


app = create_app("development")
with app.app_context():
    db = get_db()
    for table in ("tolstoy_stories", "tolstoy_system_settings", "tolstoy_users"):
        db.execute(f"DELETE FROM {table}")
    db.commit()

    bootstrap()  # seeds settings and the three admin accounts from .env
    users = seed_users(db)
    seed_stories(db, users)

    for u in users:
        db.execute("UPDATE tolstoy_users SET token_balance=? WHERE id=?",
                   (random.choice([0, 1, 2, 3, 5, 7, 10]), u["id"]))
    db.commit()

    roles = db.execute(
        "SELECT role, COUNT(*) AS c FROM tolstoy_users GROUP BY role ORDER BY role"
    ).fetchall()
    print("Seed complete:")
    for r in roles:
        print(f"  {r['role']}: {r['c']}")
    print("  stories:", db.execute("SELECT COUNT(*) FROM tolstoy_stories").fetchone()[0])
    print("  admins:", [r[0] for r in db.execute(
        "SELECT username FROM tolstoy_users WHERE role!='USER' ORDER BY id"
    ).fetchall()])
