import asyncio
from uuid import uuid4
from datetime import datetime, timezone
import bcrypt

from wenotify.db.session import AsyncSessionLocal
from wenotify.models import User, UserRole, UserStatus


def hash_password(plain_password: str) -> str:
    """Hash a password securely."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )


async def seed_first_user():
    async with AsyncSessionLocal() as session:

        result = await session.execute(User.__table__.select().limit(1))
        if result.first():
            print("Users already exist. Skipping seed.")
            return

        first_user = User(
            id=uuid4(),
            email="admin@example.com",
            username="admin",
            first_name="System",
            last_name="Administrator",
            password_hash=hash_password("ChangeMe123!"),
            is_active=True,
            status=UserStatus.ACTIVE,
            role=UserRole.ADMIN,
            permissions={},
            last_login_at=None,
            failed_login_attempts=0,
            locked_until=None,
            phone=None,
            timezone="UTC",
            preferences={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        session.add(first_user)
        await session.commit()
        print("✅ First user seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_first_user())
