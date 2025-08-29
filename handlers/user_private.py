from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command
from filters.chat_types import ChatTypeFilter

from kbds import reply


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Привет, я виртуальный помощник', 
                         reply_markup=reply.start_kb3.as_markup(
                            resize_keyboard=True,
                            input_field_placeholder='Что Вас интересует?')
                        )

    
@user_private_router.message(Command('menu'))
async def menu_cmd(message: types.Message):
    await message.answer("Вот меню:", reply_markup=reply.del_kbd)
    
    
@user_private_router.message(Command('about'))
async def menu_cmd(message: types.Message):
    await message.answer("О нас:")


@user_private_router.message(Command('payment'))
async def menu_cmd(message: types.Message):
    await message.answer("Варианты оплаты:")
    
    
@user_private_router.message(Command('shipping'))
async def menu_cmd(message: types.Message):
    await message.answer("Варианты доставки")
