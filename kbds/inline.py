from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: Optional[int] = None
    page: int = 1
    product_id: Optional[int] = None

def get_user_main_btns(*, level: int):
    keyboard = InlineKeyboardBuilder()
    
    # Первый ряд: О нас и Корзина
    keyboard.row(
        InlineKeyboardButton(text='О нас ℹ️',
                callback_data=MenuCallBack(level=level, menu_name='about').pack()),
        InlineKeyboardButton(text='Корзина 🛒',
                callback_data=MenuCallBack(level=4, menu_name='cart').pack())
    )
    
    # Второй ряд: Доставка и Оплата
    keyboard.row(
        InlineKeyboardButton(text='Доставка ⛵',
                callback_data=MenuCallBack(level=level, menu_name='shipping').pack()),
        InlineKeyboardButton(text='Оплата 💰',
                callback_data=MenuCallBack(level=level, menu_name='payment').pack())
    )
    
    # Третий ряд: Ассортимент (отдельная строка)
    keyboard.row(
        InlineKeyboardButton(text='🛍️ Ассортимент',
                callback_data=MenuCallBack(level=level+1, menu_name='catalog').pack())
    )

    return keyboard.as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                callback_data=MenuCallBack(level=level-1, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                callback_data=MenuCallBack(level=4, menu_name='cart').pack()))
    
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                callback_data=MenuCallBack(level=level+1, menu_name=c.name, category=c.id).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_products_list_btns(
    *,
    level: int,
    category: int,
    products: list,
    page: int = 1,
):
    keyboard = InlineKeyboardBuilder()

    # Первый ряд: Назад и Корзина в одной строке
    keyboard.row(
        InlineKeyboardButton(text='⬅️ Назад',
                callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()),
        InlineKeyboardButton(text='🛒 Корзина',
                callback_data=MenuCallBack(level=4, menu_name='cart').pack())
    )

    # Добавляем каждый товар в отдельном ряду
    for product in products:
        # Показываем только активные товары
        if product.is_active:
            emoji = "🟢"  # Зеленый кружок для активных товаров
            price_text = product.price
        else:
            emoji = "🔴"  # Красный кружок для неактивных
            price_text = "Нет в наличии"
            
        # Обрезаем длинное название товара
        product_name = product.name
        if len(product_name) > 25:
            product_name = product_name[:25] + "..."
            
        keyboard.row(
            InlineKeyboardButton(
                text=f"{emoji} {product_name} - {price_text}",
                callback_data=MenuCallBack(
                    level=level+1, 
                    menu_name=product.name, 
                    category=category, 
                    product_id=product.id
                ).pack()
            )
        )

    return keyboard.as_markup()


def get_products_btns(
    *,
    level: int,
    category: int,
    page: int,
    pagination_btns: dict,
    product_id: int,
):
    keyboard = InlineKeyboardBuilder()

    # Первый ряд: Назад и Корзина
    keyboard.row(
        InlineKeyboardButton(text='⬅️ Назад',
                callback_data=MenuCallBack(level=level-1, menu_name='catalog', category=category).pack()),
        InlineKeyboardButton(text='🛒 Корзина',
                callback_data=MenuCallBack(level=4, menu_name='cart').pack())
    )

    # Второй ряд: Добавить в корзину
    if product_id is not None:
        keyboard.row(
            InlineKeyboardButton(text='➕ Добавить в корзину',
                    callback_data=MenuCallBack(level=level, menu_name='add_to_cart', product_id=product_id).pack())
        )

    # Третий ряд: Ассортимент
    keyboard.row(
        InlineKeyboardButton(text='🛍️ Ассортимент',
                callback_data=MenuCallBack(level=1, menu_name='catalog').pack())
    )

    # Добавляем пагинацию только если есть кнопки
    if pagination_btns:
        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(
                            level=level,
                            menu_name=menu_name,
                            category=category,
                            page=page + 1).pack()))
            
            elif menu_name == "previous":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(
                            level=level,
                            menu_name=menu_name,
                            category=category,
                            page=page - 1).pack()))

        if row:
            keyboard.row(*row)

    return keyboard.as_markup()


def get_user_cart(
    *,
    level: int,
    page: int = None,
    pagination_btns: dict = None,
    product_id: int = None,
):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(InlineKeyboardButton(text='Удалить',
                    callback_data=MenuCallBack(level=level, menu_name='delete', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='-1',
                    callback_data=MenuCallBack(level=level, menu_name='decrement', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='+1',
                    callback_data=MenuCallBack(level=level, menu_name='increment', product_id=product_id, page=page).pack()))

        keyboard.adjust(3)

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page + 1).pack()))
            elif menu_name == "previous":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page - 1).pack()))

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(text='🏠 На главную',
                        callback_data=MenuCallBack(level=0, menu_name='main').pack()),
            InlineKeyboardButton(text='🛍️ Ассортимент',
                        callback_data=MenuCallBack(level=1, menu_name='catalog').pack()),
            InlineKeyboardButton(text='✅ Заказать',
                        callback_data=MenuCallBack(level=5, menu_name='order').pack()),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.row(
            InlineKeyboardButton(text='🏠 На главную',
                    callback_data=MenuCallBack(level=0, menu_name='main').pack()),
            InlineKeyboardButton(text='🛍️ Ассортимент',
                    callback_data=MenuCallBack(level=1, menu_name='catalog').pack())
        )
        
        return keyboard.as_markup()


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()