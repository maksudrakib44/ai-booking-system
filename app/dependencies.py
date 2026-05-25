from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.database.models import User

async def get_user_by_token(token: str | None) -> User | None:
    if not token:
        return None
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.token == token))
        user = result.scalars().first()
        if not user:
            user = User(token=token, preferences={})
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user