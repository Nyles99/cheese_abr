from aiogram.filters import Filter
from aiogram import Bot, types


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types
        
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types
    
    
class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        # Если список админов пустой, разрешаем доступ для тестирования
        if not hasattr(bot, 'my_admins_list') or not bot.my_admins_list:
            print("⚠️ Список админов пустой, разрешаем доступ")
            return True
        return message.from_user.id in bot.my_admins_list