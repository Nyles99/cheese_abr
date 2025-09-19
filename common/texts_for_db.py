from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Сыр', 'Творог', 'Масло']

description_for_info_pages = {
    "main": "Привет, я виртуальный помощник",
    "about": "О нас",
    "payment": as_marked_section(
            Bold("Варианты оплаты:"),
            "Наличные при получении",
            "Перевод на карту",
            marker="💸"
    ).as_html(),
    "shipping": "🚗 Мы с удовольствием доставим Вам нашу продукцию в удобное согласованное время. \n Доставка по Костроме бесплатная от любой суммы. ",
    'catalog': 'Категории:',
    'cart': 'В корзине ничего нет!'
}