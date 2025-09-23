from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.orm_query import orm_get_banner, orm_get_categories, orm_get_products
    
from kbds.inline import get_user_main_btns, get_user_catalog_btns, get_products_btns
from database.orm_query import Paginator

async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

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
    products = await orm_get_products(session, category_id=category)

    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}\
                </strong>\n{product.description}\nСтоимость: {product.price}\n\
                <strong>Товар {paginator.page} из {paginator.pages}</strong>",
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

async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: Optional[int] = None,
    page: Optional[int] = None,
    #product_id: int | None = None,
    #user_id: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)