"""Seed the database with initial crops and admin user.

Usage: uv run python scripts/seed.py
"""
import asyncio
import sys

sys.path.insert(0, ".")

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import session_manager
from app.modules.auth.models import User
from app.modules.crops.models import Crop

CROPS = [
    {
        "name": "Rice",
        "description": "Staple grain crop of Bangladesh, grown in three seasons: Aus, Aman, and Boro.",
        "season": "Kharif (June-November) for Aman; Rabi (Nov-April) for Boro",
        "common_diseases": "Brown Spot, Leaf Blast",
    },
    {
        "name": "Wheat",
        "description": "Winter cereal crop, second most important food grain in Bangladesh.",
        "season": "Rabi (November-April)",
        "common_diseases": "Brown Rust, Yellow Rust",
    },
    {
        "name": "Corn",
        "description": "Maize crop grown year-round in Bangladesh, used for food and animal feed.",
        "season": "Year-round; major season Rabi (Oct-March)",
        "common_diseases": "Common Rust, Gray Leaf Spot",
    },
    {
        "name": "Potato",
        "description": "Major vegetable and cash crop in Bangladesh, primarily grown in northern districts.",
        "season": "Rabi (October-March)",
        "common_diseases": "Early Blight, Late Blight",
    },
]


async def seed() -> None:
    settings = get_settings()
    async with session_manager.run():
        async with session_manager.session() as db:
            for crop_data in CROPS:
                result = await db.execute(select(Crop).where(Crop.name == crop_data["name"]))
                if not result.scalar_one_or_none():
                    db.add(Crop(**crop_data))
                    print(f"[+] Seeded crop: {crop_data['name']}")
                else:
                    print(f"[~] Crop already exists: {crop_data['name']}")

            result = await db.execute(select(User).where(User.email == "admin@fosholer.com"))
            if not result.scalar_one_or_none():
                admin = User(
                    email="admin@fosholer.com",
                    full_name="Admin User",
                    hashed_password=hash_password("admin123456"),
                    role="admin",
                )
                db.add(admin)
                print("[+] Seeded admin: admin@fosholer.com / admin123456")
            else:
                print("[~] Admin already exists")

    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
