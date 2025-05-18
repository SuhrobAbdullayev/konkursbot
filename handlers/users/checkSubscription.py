from aiogram import types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import db, bot


JOIN_PHOTO = "https://t.me/MyUzBots/251"
PHOTO_URL = "https://t.me/MyUzBots/251"

JOIN_TEXT = f"""🎄 YANGI YIL OLIMPIADASI 🎄
Ingliz tilidan bilimlaringizni sinab ko'ring va sovrinlarni qo'lga kiriting! 😊

🎁 Sovrinlar:
🥇 1-o'rin: 300 000 so'm + sertifikat
🥈 2-o'rin: 200 000 so'm + sertifikat
🥉 3-5-o'rin: 100 000 so'm + sertifikat

👉 Ishtirok etish uchun kanallarimizga obuna bo‘ling va bilimlaringizni sinang! 🏆"""
async def is_user_subscribed(user_id: int) -> bool:
    get_channels = await db.get_channels()
    if not get_channels:
        return True

    for channel_id in get_channels:
        try:
            user = await bot.get_chat_member(chat_id=channel_id['telegram_id'], user_id=user_id)
            if not user.is_chat_member():
                return False
        except Exception as e:
            print(f"Error checking subscription for channel {channel_id}: {e}")
            return False
    return True

async def check_subscription(message: types.Message):
    user_id = message.from_user.id
    get_channels = await db.get_channels()

    if not get_channels:
        return True

    is_subscribed = await is_user_subscribed(user_id)
    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(row_width=1)
        for get_channel in get_channels:
            channel_button = InlineKeyboardButton(text=get_channel['name'], url=get_channel['invite_link'])
            keyboard.add(channel_button)
        check_button = InlineKeyboardButton(text="Done ✅", callback_data="check_subscription")
        keyboard.add(check_button)

        await message.answer_photo(JOIN_PHOTO, caption=JOIN_TEXT, reply_markup=keyboard, parse_mode="HTML")
        return False
    return True