from fastapi import Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.database.models import User

async def get_user_by_token(
    x_user_token: str = Header(None, alias="X-User-Token"),
    db: AsyncSession = Depends(get_db)
):
    if not x_user_token:
        return None

    result = await db.execute(select(User).where(User.token == x_user_token))
    user = result.scalars().first()

    if not user:
        user = User(token=x_user_token, preferences={})
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user