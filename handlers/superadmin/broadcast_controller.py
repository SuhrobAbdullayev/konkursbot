import asyncio
import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentTypes
from aiogram.utils import exceptions

from data.config import ADMINS
from filters import IsSuperAdmin
from keyboards.inline.superAdminKeyboards import cancel
from loader import db, dp, bot


@dp.callback_query_handler(IsSuperAdmin(), text="superadmin:send_ads", state="*")
async def send_ads(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.edit_text("Xabarni yuboring:", reply_markup=cancel)
    await state.set_state("superadmin:ads:get")


@dp.message_handler(IsSuperAdmin(), state="superadmin:ads:get", content_types=ContentTypes.ANY)
async def send_message(message: Message, state: FSMContext):
    await db.add(table_name="ads", fields={"chat_id": str(message.chat.id),
                                           "from_chat_id": str(message.chat.id),
                                           "message_id": str(message.message_id)}
                 )
    ads_info = await db.select(table_name="ads", fields="*",
                               condition=f"WHERE chat_id = '{message.chat.id}' AND message_id = '{message.message_id}'")
    await db.need_send_ads_to_users(ads_id=ads_info[0]['id'])
    await message.answer("✅ Xabar yuborish boshlandi...")
    await state.finish()
    await state.reset_state()


async def send_ads_with_task(users: list) -> bool:
    success = 0
    removed = 0
    for user in users:
        try:
            await bot.forward_message(chat_id=user['telegram_id'], from_chat_id=user["from_chat_id"],
                                      message_id=user["message_id"])
            await db.delete(table_name="user_ads", condition=f"user_id = {user['user_id']} AND ads_id = {user['ads_id']}")
            logging.info(f"Message sent to {user['telegram_id']}")
            success += 1
        except exceptions.BotBlocked:
            await db.delete(table_name="users", condition=f"telegram_id = '{user['telegram_id']}'")
            await db.delete(table_name="user_ads", condition=f"user_id = {user['user_id']} AND ads_id = {user['ads_id']}")
            removed += 1
        except exceptions.ChatNotFound:
            await db.delete(table_name="users", condition=f"telegram_id = '{user['telegram_id']}'")
            await db.delete(table_name="user_ads", condition=f"user_id = {user['user_id']} AND ads_id = {user['ads_id']}")
            removed += 1
        except exceptions.RetryAfter as e:
            await bot.send_message(chat_id=ADMINS[0],
                                   text=f"⚠️ Xabar yuborish {e.timeout} soniyadan keyn davom etadi...")
            await asyncio.sleep(e.timeout)
            await bot.forward_message(chat_id=user['telegram_id'], from_chat_id=user["from_chat_id"],
                                      message_id=user["message_id"])
            await bot.send_message(chat_id=ADMINS[0], text=f"✅ xabar yuborish davom ettirildi.")
            await db.delete(table_name="user_ads", condition=f"user_id = {user['user_id']} AND ads_id = {user['ads_id']}")
            success += 1
        except exceptions.UserDeactivated:
            await db.delete(table_name="users", condition=f"telegram_id = '{user['telegram_id']}'")
            await db.delete(table_name="user_ads", condition=f"user_id = {user['user_id']} AND ads_id = {user['ads_id']}")
            removed += 1
        except exceptions.CantInitiateConversation:
            await db.delete(table_name="users", condition=f"telegram_id = '{user['telegram_id']}'")
            await db.delete(table_name="user_ads", condition=f"user_id = {user['user_id']} AND ads_id = {user['ads_id']}")
            removed += 1
        except Exception as e:
            await db.delete(table_name="user_ads", condition=f"user_id = {user['user_id']} AND ads_id = {user['ads_id']}")
            await db.delete(table_name="users", condition=f"telegram_id = '{user['telegram_id']}'")
    return True
        