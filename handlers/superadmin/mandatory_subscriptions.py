from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatType, ContentTypes, Message
from filters import IsSuperAdmin
from loader import db, dp, bot


@dp.callback_query_handler(IsSuperAdmin(), text="superadmin:mandatory_subscriptions", state="*")
async def mandatory_subscriptions_function(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)

    channels = await db.select(table_name="channels", fields="*")
    channels_kb = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        channels_kb.add(InlineKeyboardButton(
            text=f"{channel['name']}", callback_data=f"superadmin:ms:{channel['id']}")
        )
    channels_kb.add(
        InlineKeyboardButton(text="➕ Yangi Kanal qo'shish",
                             url=f"https://telegram.me/{(await bot.me).username}?startchannel"),
        InlineKeyboardButton(text="♻️ Tekshirish", callback_data="check_subscriptions"),
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="superadmin:cancel")
    )
    await call.message.edit_text("Majburiy obunalar ro'yxati:", reply_markup=channels_kb)

    # Xatolardan himoyalangan state.finish()
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
    except KeyError:
        pass


@dp.callback_query_handler(IsSuperAdmin(), text="check_subscriptions", state="*", chat_type=ChatType.PRIVATE)
async def check_subscriptions(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.edit_text("Kanal id raqamini kiriting\n"
                                 "Masalan: -1001234567890\n"
                                 "@getmyid_bot orqali kanal id raqamini olishingiz mumkin")
    await state.set_state("superadmin:check_subscriptions")


@dp.message_handler(IsSuperAdmin(), state="superadmin:check_subscriptions", content_types=ContentTypes.TEXT)
async def check_subscriptions(message: Message, state: FSMContext):
    await message.delete()
    chat_id = message.text
    try:
        channel_data = await bot.get_chat(chat_id=chat_id)
        channel_name = channel_data.title
        invite_link = channel_data.invite_link

        await db.add(
            table_name="channels",
            fields={
                "telegram_id": str(chat_id),
                "name": channel_name,
                "invite_link": invite_link
            }
        )

        await message.answer(
            text="✅ Kanal/Guruh muvaffaqiyatli qo'shildi!",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="superadmin:mandatory_subscriptions")
            )
        )

    except Exception as e:
        print(e)
        await message.answer(
            text="❌ Kanal/Guruh qo'shilmadi!\n"
                 "Sabab: Kanal/Guruhni botga admin qilinmagan, ID raqam noto'g'ri yoki bu kanal/guruh allaqachon mavjud!"
        )
    finally:
        try:
            current_state = await state.get_state()
            if current_state is not None:
                await state.finish()
                await state.reset_data()
        except KeyError:
            pass


@dp.callback_query_handler(text_contains="superadmin:ms:", state="*")
async def delete_chat(call: CallbackQuery):
    await call.answer(cache_time=1)
    chat_id = call.data.split(":")[-1]
    confirm_kb = InlineKeyboardMarkup(row_width=1)
    confirm_kb.add(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"smsc:{chat_id}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="superadmin:mandatory_subscriptions")
    )
    await call.message.edit_text(
        text="❗️ Siz majburiy obunani o'chirmoqchisiz!\n"
             "✅ O'chirish uchun 'Tasdiqlash' tugmasini bosing!",
        reply_markup=confirm_kb
    )


@dp.callback_query_handler(text_contains="smsc:", state="*")
async def delete_chat(call: CallbackQuery):
    await call.answer(cache_time=1)
    chat_id = call.data.split(":")[-1]
    await db.delete(table_name="channels", condition=f"id='{chat_id}'")
    await call.message.edit_text(
        text="✅ Chat muvaffaqiyatli o'chirildi!",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="superadmin:mandatory_subscriptions")
        )
    )
