from __future__ import annotations
import re
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from loader import db

VALID_PREFIXES = {
    "33", "50", "55", "70", "71", "72", "73", "74", "75",
    "77", "78", "79", "88", "90", "91", "93", "94", "95", "97", "98", "99"
}

def format_uzbek_number_strict(text: str) -> str | None:
    if re.search(r"[a-zA-Z]", text):
        return None

    digits = re.sub(r"\D", "", text)

    if digits.startswith("998") and len(digits) == 12:
        core = digits[3:]
    elif len(digits) == 9:
        core = digits
    else:
        return None

    prefix = core[:2]
    if prefix not in VALID_PREFIXES:
        return None

    return f"+998 {core[:2]} {core[2:5]} {core[5:7]} {core[7:9]}"

async def check_phone_number(message: types.Message) -> bool:
    info = await db.select_info(str(message.from_user.id))

    if info['phone']:
        phone_number = None

        if message.contact:
            phone_number = message.contact.phone_number
        elif message.text:
            phone_number = message.text

        formatted_number = format_uzbek_number_strict(phone_number or "")
        if formatted_number:
            return True
        else:
            await message.answer("❌ Telefon raqamingiz noto‘g‘ri. Iltimos, faqat O‘zbekiston raqamini kiriting.")
            return False

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))

    await message.answer(
        "📱 Telefon raqamingizni yozib yuboring.\n\nMasalan: +998901234567\n\nYoki telefon raqamni yuborish tugmasini bosing:",
        reply_markup=keyboard
    )
    return False
