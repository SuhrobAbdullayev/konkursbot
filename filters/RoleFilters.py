from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from data.config import ADMINS
from loader import db
from utils.misc.functions import get_user_data


async def check_user(table_name, user_id):
    return await db.select(table_name=table_name, fields="*", condition=f"WHERE telegram_id = '{user_id}'")


class IsSuperAdmin(BoundFilter):
    async def check(self, message: Message):
        return str(message.from_user.id) in ADMINS


class IsUser(BoundFilter):
    async def check(self, message: Message):
        return bool(await get_user_data(user_id=message.from_user.id))

