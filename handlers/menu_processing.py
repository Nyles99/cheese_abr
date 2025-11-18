import asyncio
import datetime
import types
import os
from aiogram.types import InputMediaPhoto, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from database.orm_query import (
    orm_add_to_cart,
    orm_delete_from_cart,
    orm_get_active_products,
    orm_get_banner,
    orm_get_categories,
    orm_get_products,
    orm_get_user_carts,
    orm_reduce_product_in_cart,
    orm_clear_cart,
)
from kbds.inline import (
    get_products_btns,
    get_user_cart,
    get_user_catalog_btns,
    get_user_main_btns,
)
from database.orm_query import Paginator

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main_menu(session, level, menu_name):
    
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds


async def get_user_info_string(bot: Bot, user_id: int) -> str:
    """
    Возвращает строку с полной информацией о пользователе
    """
    try:
        user = await bot.get_chat(user_id)
        
        full_name = user.full_name or "Не указано"
        username_1 = f"@{user.username}" if user.username else "Не указан"
        
        return f"{full_name} ({username_1})"
        
    except Exception as e:
        print(f"Ошибка получения информации о пользователе {user_id}: {e}")
        return "Пользователь (Не указан)"


async def main_cart_menu(session, level, menu_name, user_id):
    bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Получаем информацию о пользователе и его телефон
    from database.orm_query import orm_get_user
    user = await orm_get_user(session, user_id)
    user_name = await get_user_info_string(bot, user_id)
    
    # Получаем корзину
    cartss = await orm_get_user_carts(session, user_id)
    spisok = ''
     
    if cartss:
        for cart_item in cartss:
            print(cart_item.product.name)
            spisok = spisok + f'{cart_item.product.name} - {cart_item.quantity} штук. \n'
    
    # Формируем сообщение для менеджера с телефоном
    phone_info = user.phone if user and user.phone else "❌ Не указан"
    
    try:
        await bot.send_message(
            chat_id=992900169,
            text=f"🚀 *НОВЫЙ ЗАКАЗ!*\n\n"
                 f"👤 Покупатель: {user_name}\n"
                 f"📞 Телефон: {phone_info}\n"
                 f"🆔 ID: `{user_id}`\n"
                 f"📅 Время: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                 f"🛒 Состав заказа:\n{spisok}",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка отправки менеджеру: {e}")
    
    await orm_clear_cart(session, user_id)
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption="✅ Ваш заказ принят! Ожидайте подтверждения. Продолжим покупки?")
    level = 0
    kbds = get_user_main_btns(level=level)
    
    return image, kbds


async def catalog(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def products(session, level, category, page):
    # Используем старую функцию, которая возвращает ВСЕ товары
    products = await orm_get_products(session, category_id=category)

    # Проверяем, есть ли товары в категории
    if not products:
        # Если товаров нет, возвращаем специальный флаг
        return "empty_category", None

    paginator = Paginator(products, page=page)
    
    # Проверяем, что страница не пустая
    current_page = paginator.get_page()
    if not current_page:
        # Если страница пустая, возвращаемся на первую страницу
        page = 1
        paginator = Paginator(products, page=page)
        current_page = paginator.get_page()
    
    product = current_page[0]

    # Формируем подпись в зависимости от доступности товара
    if product.is_active:
        caption = f"<strong>{product.name}</strong>\n{product.description}\nСтоимость: {product.price}\n<strong>Товар {paginator.page} из {paginator.pages}</strong>"
    else:
        caption = f"<strong>{product.name}</strong>\n{product.description}\n<strong>❌ Нет в наличии</strong>\n<strong>Товар {paginator.page} из {paginator.pages}</strong>"

    image = InputMediaPhoto(
        media=product.image,
        caption=caption,
    )

    pagination_btns = pages(paginator)

    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )

    return image, kbds


async def carts(session, level, menu_name, page, user_id, product_id):
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, product_id)
    
    
    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(
            media=banner.image, caption=f"<strong>{banner.description}</strong>"
        )

        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )

    else:
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]
        cart_price = int(cart.product.price[: cart.product.price.find('₽')]) * cart.quantity
        total_price = sum(cart.quantity * int(cart.product.price[: cart.product.price.find('₽')]) for cart in carts)
        
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.name}</strong>\n{cart.product.price} x {cart.quantity} = {cart_price}₽ \
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\nОбщая стоимость товаров в корзине {total_price}₽",
        )

        pagination_btns = pages(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: Optional[int] = None,
    page: Optional[int] = None,
    product_id: Optional[int] = None,
    user_id: Optional[int] = None,
    
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)
    elif level == 4:
        return await main_cart_menu(session, level, 'main', user_id)