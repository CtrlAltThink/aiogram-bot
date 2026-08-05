from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_shift
from kbds.reply import get_keyboard

user_private_router = Router()

USER_MAIN_KB=get_keyboard(
                            'Добавить смену',
                            'Зарплата',
                            'История',
                            'Настройка кранов',
                            'Настройки профиля',
                            'Помощь',
                            'Главное меню',
                            placeholder='Что вас интересует?',
                            sizes=(2, 2, 2)
                        )

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет, я виртуальный помощник!", 
                         reply_markup=USER_MAIN_KB)

class AddShift(StatesGroup):
    hours = State()

@user_private_router.message(StateFilter(None), F.text.lower() == 'добавить смену')
async def add_shift(message: types.Message, state: FSMContext):
    await message.answer(
        'Введите количество часов:', reply_markup=get_keyboard('Отмена', sizes=(1,))
    )
    await state.set_state(AddShift.hours)

@user_private_router.message(StateFilter('*'), Command('отмена'))
@user_private_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
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
    await state.update_data(hours=hours, user_id=message.from_user.id)
    data = await state.get_data()
    await orm_add_shift(session, data)
    await message.answer('Часы добавлены', reply_markup=USER_MAIN_KB)
    await state.clear()


@user_private_router.message(F.text.lower() == 'зарплата')
@user_private_router.message(Command('salary'))
async def salary(message: types.Message) -> None:
    await message.answer('Ваша прогнозируемая ЗП:')

@user_private_router.message(F.text.lower() == 'история')
@user_private_router.message(Command('history'))
async def history(message: types.Message) -> None:
    await message.answer('История смен:')

@user_private_router.message(F.text.lower() == 'настройка кранов')
@user_private_router.message(Command('crane_help'))
async def crane_help(message: types.Message) -> None:
    await message.answer('Настройка кранов')

@user_private_router.message(F.text.lower() == 'настройки профиля')
@user_private_router.message(Command('settings'))
async def settings(message: types.Message) -> None:
    await message.answer('Настройки профиля:')

@user_private_router.message(F.text.lower() == 'помощь')
@user_private_router.message(Command('help'))
async def help(message: types.Message) -> None:
    await message.answer('Вот помощь:')

# @user_private_router.message((F.text.lower() == 'Главное меню'))
@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'главное меню')))
async def menu_cmd(message: types.Message) -> None:
    await message.answer('Вы в главном меню:')