from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from filters import IsSuperAdmin
from loader import dp, db

back = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="superadmin:cancel")
        ]
    ]
)


@dp.callback_query_handler(IsSuperAdmin(), text="superadmin:active_0", state="*")
async def active_0(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_text(text="✅ Barcha foydalanuvchilar aktivligi 0 ga tushirildi", reply_markup=back)


@dp.callback_query_handler(IsSuperAdmin(), text="superadmin:stat", state="*")
async def show_stat(call: CallbackQuery):
    await call.answer(cache_time=1)
    query = """
            SELECT
                'total_users' AS type,
                COUNT(*) AS count
            FROM
                users
            UNION ALL
            SELECT
                'active_users' AS type,
                COUNT(*) AS count
            FROM
                users
            WHERE
                status = True
            UNION ALL
            SELECT
                'daily_users' AS type,
                COUNT(*) AS count
            FROM
                users
            WHERE
                created_at > now() - interval '1 day'
            UNION ALL
            SELECT
                'weekly_users' AS type,
                COUNT(*) AS count
            FROM
                users
            WHERE
                created_at > now() - interval '7 day'
            UNION ALL
            SELECT
                'monthly_users' AS type,
                COUNT(*) AS count
            FROM
                users
            WHERE
                created_at > now() - interval '30 day'
            UNION ALL 
            SELECT 
                'ads' AS type,
                COUNT(*) AS count
            FROM user_ads
        """

    results = await db.execute(query, fetch=True)
    data = {result['type']: result['count'] for result in results}
    text = f"""
📊 Foydalanuvchilar:

    👤 Ja'mi: {data.get('total_users', 0)} ta
    👤 Aktiv: {data.get('active_users', 0)} ta
    📆 Bugun: {data.get('daily_users', 0)} ta
    📆 Hafta: {data.get('weekly_users', 0)} ta
    📆 Oy: {data.get('monthly_users', 0)} ta
    📆 Reklama: {data.get('ads', 0)} ta userga yuborilishi kerak
"""

    await call.message.edit_text(text=text, reply_markup=back)
