from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu_super_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="superadmin:stat"),
        ],
        [
            InlineKeyboardButton(text="📝 Reklama yuborish", callback_data="superadmin:send_ads"),
        ],
        [
            InlineKeyboardButton(text="📢 Majburiy Obunalar", callback_data="superadmin:mandatory_subscriptions"),
        ]
    ]
)

cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="superadmin:cancel")
        ]
    ]
)

back = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="superadmin:cancel")
        ]
    ]
)
