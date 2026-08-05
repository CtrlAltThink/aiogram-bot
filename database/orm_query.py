from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Shift


async def orm_add_shift(session: AsyncSession, data: dict):
    obj = Shift(
        user_id=data['user_id'],
        date=datetime.now(timezone.utc).date(),
        hours=data['hours'],
    )
    session.add(obj)
    await session.commit()