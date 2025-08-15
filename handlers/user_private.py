from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Привет, я виртуальный помощник')

    
@user_private_router.message(Command('menu'))
async def menu_cmd(message: types.Message):
    await message.answer("Вот меню:")
    
    
@user_private_router.message(Command('about'))
async def menu_cmd(message: types.Message):
    await message.answer("О нас:")


@user_private_router.message(Command('payment'))
async def menu_cmd(message: types.Message):
    await message.answer("Варианты оплаты:")
    
    
@user_private_router.message(Command('shipping'))
async def menu_cmd(message: types.Message):
    await message.answer("Варианты доставки")
    
    
@user_private_router.message(F.text)
async def menu_cmd(message: types.Message):
    await message.answer("Это магический фильтр")