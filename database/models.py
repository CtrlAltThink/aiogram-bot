from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    base_salary: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)

class Shift(Base):
    __tablename__ = 'shifts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[int] = mapped_column(Integer, nullable=False)