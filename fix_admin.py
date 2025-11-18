# fix_admin.py
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.engine import session_maker
from database.orm_query import orm_add_user

async def create_admin_user():
    """Создает тестового пользователя админа"""
    async with session_maker() as session:
        # Добавляем пользователя с ID который есть в my_admins_list
        await orm_add_user(
            session,
            user_id=992900169,  # Ваш ID менеджера
            first_name="Admin",
            last_name="User",
            phone="+79991234567"
        )
        print("✅ Админ пользователь создан")

if __name__ == "__main__":
    asyncio.run(create_admin_user())