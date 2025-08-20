from aiogram.filters import Filter
from aiogram import types


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types
        
    async def __call__(self, messages: types.Message):
        return super().__call__(*args, **kwds)