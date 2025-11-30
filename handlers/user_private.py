from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_add_to_cart,
    orm_add_user,
    orm_get_user,
    orm_save_user_phone,
)

from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from kbds.inline import MenuCallBack, get_callback_btns
import re

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

class UserInfo(StatesGroup):
    waiting_for_phone = State()

def validate_phone(phone: str) -> bool:
    """Проверка формата номера телефона"""
    pattern = r'^\+7\d{10}$'
    return bool(re.match(pattern, phone))

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)

async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    
    # Проверяем доступность товара
    from database.orm_query import orm_get_product
    product = await orm_get_product(session, callback_data.product_id)
    
    if not product or not product.is_active:
        await callback.answer("❌ Данного товара нет в наличии", show_alert=True)
        return
    
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("Товар добавлен в корзину.")

async def process_order_with_phone_check(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    """Проверяем телефон и переходим к заказу"""
    user_id = callback.from_user.id
    user = await orm_get_user(session, user_id)
    
    if user and user.phone:
        # Телефон есть - переходим к оформлению заказа
        media, reply_markup = await get_menu_content(
            session,
            level=5,  # Уровень для оформления заказа
            menu_name="order",
            user_id=user_id,
        )
        await callback.message.edit_media(media=media, reply_markup=reply_markup)
    else:
        # Телефона нет - запрашиваем его
        await callback.message.answer(
            "📞 Для оформления заказа нам нужен ваш номер телефона.\n\n"
            "Отправьте номер телефона в формате: +79991234567\n"
            "Или нажмите кнопку ниже, чтобы поделиться номером:",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="📱 Поделиться номером", request_contact=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        await state.set_state(UserInfo.waiting_for_phone)
        await callback.answer()

# Обработчик получения номера телефона
@user_private_router.message(UserInfo.waiting_for_phone, F.contact | F.text)
async def get_user_phone(message: types.Message, state: FSMContext, session: AsyncSession):
    phone = None
    
    if message.contact:
        # Получили номер через кнопку "Поделиться номером"
        phone = message.contact.phone_number
    elif message.text:
        # Получили номер текстом
        if validate_phone(message.text):
            phone = message.text
        else:
            await message.answer("❌ Неверный формат номера. Используйте формат: +79991234567")
            return
    
    if phone:
        # Сохраняем номер в базу
        user_id = message.from_user.id
        await orm_save_user_phone(session, user_id, phone)
        
        # Убираем клавиатуру
        await message.answer("✅ Номер сохранен! Оформляем заказ...", 
                           reply_markup=types.ReplyKeyboardRemove())
        
        # Переходим к оформлению заказа
        media, reply_markup = await get_menu_content(
            session,
            level=5,  # Уровень для оформления заказа
            menu_name="order", 
            user_id=user_id,
        )
        await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)
        
        await state.clear()

@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession, state: FSMContext):

    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return

    # Обработка кнопки заказа (проверка телефона)
    if callback_data.menu_name == "order":
        await process_order_with_phone_check(callback, session, state)
        return

    # Определяем правильный уровень и параметры для навигации
    target_level = callback_data.level
    target_menu_name = callback_data.menu_name
    target_category = callback_data.category
    target_page = callback_data.page
    target_product_id = callback_data.product_id

    # Специальная обработка для перехода из списка товаров к конкретному товару
    if callback_data.level == 2 and callback_data.product_id:
        # Это клик на конкретный товар из списка
        target_level = 3  # Переходим на уровень детального просмотра
        target_menu_name = "product_detail"
    
    # Специальная обработка для перехода из категории в список товаров
    elif callback_data.level == 1 and callback_data.menu_name != "catalog":
        # Это выбор категории из каталога
        target_level = 2  # Переходим на уровень списка товаров
        target_menu_name = "products_list"

    media, reply_markup = await get_menu_content(
        session,
        level=target_level,
        menu_name=target_menu_name,
        category=target_category,
        page=target_page,
        product_id=target_product_id,
        user_id=callback.from_user.id,
    )

    # Обработка случая когда категория пустая
    if media == "empty_category":
        await callback.answer("В этой категории отсутствует товар на данный момент, возможно, все уже съели) 🧀", show_alert=False)
        return

    # Обработка случая когда товар не найден
    if media == "product_not_found":
        await callback.answer("❌ Товар не найден", show_alert=True)
        return

    # Обработка случая когда нет медиа (для уровня 5 - оформление заказа)
    if media is None and target_level == 5:
        await callback.message.answer(
            "✅ Ваш заказ принят! Ожидайте подтверждения. Продолжим покупки?",
            reply_markup=reply_markup
        )
        return

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()