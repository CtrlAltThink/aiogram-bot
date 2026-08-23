from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Shift, User


async def orm_get_user(session: AsyncSession, telegram_id):
    query = select(User).where(User.telegram_id == telegram_id)
    return await session.scalar(query)

async def orm_add_user(session: AsyncSession, telegram_id, first_name, last_name, base_salary):
    query = select(User).where(User.telegram_id == telegram_id)
    user = await session.scalar(query)
    if user:
        return
    else:
        obj = User(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            base_salary=base_salary,
            )
        session.add(obj)
        await session.commit()

async def orm_add_shift(session: AsyncSession, user_id: int, hours: int):
    stmt = insert(Shift).values(user_id=user_id,
                                date=datetime.now(timezone.utc).date(),
                                hours=hours,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id', 'date'],
        set_={'hours': hours}
    )
    await session.execute(stmt)
    await session.commit()

async def orm_update_user_salary(session: AsyncSession, user_id: int, new_user_salary: float):
    stmt = (
        update(User).where(User.telegram_id == user_id).values(base_salary=new_user_salary)
    )
    await session.execute(stmt)
    await session.commit()