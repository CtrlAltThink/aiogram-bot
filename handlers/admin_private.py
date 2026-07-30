from aiogram import F, Router, types
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboard(
    'Посмотреть информацию о пользователях',
    'Главное меню',
    placeholder='Выберете действие',
    sizes=(1,1,)
)

@admin_router.message(Command('admin'))
async def starting_admin_panel(message: types.Message):
    await message.answer('Что хотите сделать?', reply_markup=ADMIN_KB)

@admin_router.message(F.text == 'Посмотреть информацию о пользователях')
async def user_info(message: types.Message):
    await message.answer('Список пользователей')

@admin_router.message(F.text.lower() == 'главное меню')
async def menu_cmd(message: types.Message) -> None:
    await message.answer('Вы в главном меню:')