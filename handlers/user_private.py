from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f

from kbds.reply import get_keyboard

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет, я виртуальный помощник!", 
                         reply_markup=get_keyboard(
                             'Добавить смену',
                             'Зарплата',
                             'История',
                             'Настройка кранов',
                             'Настройки профиля',
                             'Главное меню',
                             placeholder='Что вас интересует?',
                             sizes=(2, 2, 2)
                        ),
                    )

@user_private_router.message((F.text.lower() == 'добавить смену'))
@user_private_router.message(Command('add_shift'))
async def add_shift(message: types.Message) -> None:
    await message.answer('Вот смена:')

@user_private_router.message((F.text.lower() == 'зарплата'))
@user_private_router.message(Command('salary'))
async def salary(message: types.Message) -> None:
    await message.answer('Ваша прогнозируемая ЗП:')

@user_private_router.message((F.text.lower() == 'история'))
@user_private_router.message(Command('history'))
async def history(message: types.Message) -> None:
    await message.answer('История смен:')

@user_private_router.message((F.text.lower() == 'настройка кранов'))
@user_private_router.message(Command('crane_help'))
async def crane_help(message: types.Message) -> None:
    await message.answer('Настройка кранов')

@user_private_router.message((F.text.lower() == 'настройки профиля'))
@user_private_router.message(Command('settings'))
async def settings(message: types.Message) -> None:
    await message.answer('Настройки профиля:')

# @user_private_router.message((F.text.lower() == 'Главное меню'))
@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'главное меню')))
async def menu_cmd(message: types.Message) -> None:
    await message.answer('Вы в главном меню:')