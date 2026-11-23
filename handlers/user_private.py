import calendar
import logging
from datetime import datetime, timezone

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_add_shift,
    orm_add_user,
    orm_get_this_month_hours,
    orm_get_user,
    orm_update_user_salary,
)
from kbds.reply import get_keyboard

logger = logging.getLogger(__name__)

user_private_router = Router()

USER_MAIN_KB=get_keyboard(
                            'Записать / Изменить смену',
                            'Зарплата',
                            'История',
                            'Настройка кранов',
                            'Изменить оклад',
                            'Помощь',
                            'Главное меню',
                            placeholder='Что вас интересует?',
                            sizes=(1, 2, 2)
                        )



class Registration(StatesGroup):
    base_salary = State()

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    if await orm_get_user(session, message.from_user.id):
        await message.answer(f"Привет {message.from_user.first_name}, я виртуальный помощник!", 
                             reply_markup=USER_MAIN_KB)
    else:
        await message.answer(
            'Введите свой месячный оклад: '
        )
        await state.set_state(Registration.base_salary)


@user_private_router.message(Registration.base_salary, F.text)
async def process_salary(message: types.Message, state: FSMContext, session: AsyncSession):
    if not message.text.isdigit():
        await message.answer('Введите целое число!')
        return
    salary = int(message.text)
    if salary <= 0:
        await message.answer('Число должно быть больше нуля!')
        return
    try:
        await orm_add_user(session, message.from_user.id, message.from_user.first_name, message.from_user.last_name, salary)
        await state.clear()
        await message.answer(f"Оклад добавлен, его можно изменить в настройках.\n"
                             f"Привет {message.from_user.first_name}, я виртуальный помощник!", 
                                     reply_markup=USER_MAIN_KB)
    except SQLAlchemyError:
        logger.exception('Ошибка при работе с БД для пользователя telegram_id=%s', message.from_user.id)
        await state.clear()
        await message.answer('Ошибка базы данных, напишите в поддержку.', reply_markup=USER_MAIN_KB)



class AddShift(StatesGroup):
    hours = State()

@user_private_router.message(StateFilter(None), F.text.lower() == 'записать / изменить смену')
async def add_shift(message: types.Message, state: FSMContext):
    await message.answer(
        'Введите количество часов за сегодня. '
        'Если за сегодня смена уже существует, часы обновятся на новое значение.', 
        reply_markup=get_keyboard('Отмена', sizes=(1,))
    )
    await state.set_state(AddShift.hours)

@user_private_router.message(StateFilter('*'), Command('отмена'))
@user_private_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_add_shift(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Действия отменены!', reply_markup=USER_MAIN_KB)

@user_private_router.message(AddShift.hours, F.text)
async def process_hours(message: types.Message, state: FSMContext, session: AsyncSession):

    if not message.text.isdigit():
        await message.answer('Введите целое число!')
        return
    hours = int(message.text)
    if hours < 1 or hours > 24:
        await message.answer('Число должно быть от 1 до 24!')
        return
    try:
        await orm_add_shift(session, message.from_user.id, hours)
        await message.answer('Часы добавлены.', reply_markup=USER_MAIN_KB)
        await state.clear()
    except SQLAlchemyError:
        logger.exception('Ошибка при работе с БД для пользователя telegram_id=%s', message.from_user.id)
        await state.clear()
        await message.answer('Ошибка базы данных, напишите в поддержку.', reply_markup=USER_MAIN_KB)



@user_private_router.message(F.text.lower() == 'зарплата')
@user_private_router.message(Command('salary'))
async def salary(message: types.Message, session: AsyncSession) -> None:
    hours = await orm_get_this_month_hours(session, message.from_user.id)
    user = await orm_get_user(session, message.from_user.id)
    now = datetime.now(timezone.utc)
    current_year = now.year
    current_month = now.month
    _, days_in_month = calendar.monthrange(current_year, current_month)
    work_days = 0
    for day in range(1, days_in_month + 1):
        if calendar.weekday(current_year, current_month, day) < 5:
            work_days += 1
    month_norm_hours = work_days * 8
    hourly_rate = user.base_salary / month_norm_hours if month_norm_hours > 0 else 0
    earned_salary = hours * hourly_rate
    await message.answer(f'Отработано в этом месяце: {hours} ч.')
    await message.answer(f'Базовый оклад: {int(user.base_salary)} руб.')
    await message.answer(f'За этот месяц вы получите: {round(earned_salary, 2)} руб.')


@user_private_router.message(F.text.lower() == 'история')
@user_private_router.message(Command('history'))
async def history(message: types.Message) -> None:
    await message.answer('История смен:')

@user_private_router.message(F.text.lower() == 'настройка кранов')
@user_private_router.message(Command('crane_help'))
async def crane_help(message: types.Message) -> None:
    await message.answer('Настройка кранов')



class EditSalary(StatesGroup):
    salary = State()
@user_private_router.message(StateFilter(None), F.text.lower() == 'изменить оклад')
async def edit_salary(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        'Введите оклад:',
        reply_markup=get_keyboard('Отмена', sizes=(1,))
    )
    await state.set_state(EditSalary.salary)

@user_private_router.message(EditSalary.salary, F.text)
async def process_edit_salary(message: types.Message, state: FSMContext, session: AsyncSession):

    if not message.text.isdigit():
            await message.answer('Введите целое число!')
            return
    salary = int(message.text)
    if salary < 1:
        await message.answer('Число должно быть положительным!')
        return
    try:
        await orm_update_user_salary(session, message.from_user.id, salary)
        await message.answer('Оклад изменён.', reply_markup=USER_MAIN_KB)
        await state.clear()
    except SQLAlchemyError:
        logger.exception('Ошибка при работе с БД для пользователя telegram_id=%s', message.from_user.id)
        await state.clear()
        await message.answer('Ошибка базы данных, напишите в поддержку.', reply_markup=USER_MAIN_KB)
    


@user_private_router.message(F.text.lower() == 'помощь')
@user_private_router.message(Command('help'))
async def help(message: types.Message) -> None:
    await message.answer('Вот помощь:')

# @user_private_router.message((F.text.lower() == 'Главное меню'))
@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'главное меню')))
async def menu_cmd(message: types.Message) -> None:
    await message.answer('Вы в главном меню:')