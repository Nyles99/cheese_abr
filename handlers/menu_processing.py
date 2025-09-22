from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_banner
    
from kbds.inline import get_user_main_btns


async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds

async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    #category: int | None = None,
    #page: int | None = None,
    #product_id: int | None = None,
    #user_id: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)