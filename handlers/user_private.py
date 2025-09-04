from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.formatting import as_list, as_marked_section, Bold

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_products

from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет, я виртуальный помощник",
        reply_markup=get_keyboard(
            "Ассортимент",
            "О нас",
            "Варианты оплаты",
            "Доставка",
            placeholder="Что вас интересует?",
            sizes=(2, 2)
        ),
    )

@user_private_router.message(F.text.lower() == "ассортимент")    
@user_private_router.message(Command('menu'))
async def menu_cmd(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {product.price}"
        )
    await message.answer("Вот ассортимент:")
    
@user_private_router.message(F.text.lower() == 'о нас')    
@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer("О нас:")


@user_private_router.message(F.text.lower() == 'варианты оплаты')
@user_private_router.message(Command('payment'))
async def payment_cmd(message: types.Message):
    
    text = as_marked_section(
            Bold("Варианты оплаты:"),
            "Наличные при получении",
            "Перевод на карту",
            marker="💸"
        )
    await message.answer(text.as_html())
    
@user_private_router.message(F.text.lower() == 'доставка')    
@user_private_router.message(Command('shipping'))
async def shipping_cmd(message: types.Message):
    await message.answer("🚗 Мы с удовольствием доставим Вам нашу продукцию в удобное согласованное время. \n Доставка по Костроме бесплатная от любой суммы. ")
    

@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer(f"номер получен")
    await message.answer(str(message.contact))
    
    
@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer(f"локация получена")
    await message.answer(str(message.location))