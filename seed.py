import asyncio
from uuid import uuid4
from datetime import datetime, timezone
import bcrypt

from wenotify.db.session import AsyncSessionLocal
from wenotify.models import User, UserRole, UserStatus


def hash_password(plain_password: str) -> str:
    """Hash a password securely."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def seed_first_user():
    async with AsyncSessionLocal() as session:

        result = await session.execute(User.__table__.select().limit(1))
        if result.first():
            print("Users already exist. Skipping seed.")
            return

        first_user = User(
            id=uuid4(),
            email="admin@gmail.com",
            phone_number="+254700000000",
            password_hash=hash_password("Password@1"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_verified=True,
            is_active=True,
            email_verified=True,
            phone_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        session.add(first_user)
        await session.commit()
        print("✅ First user seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_first_user())
