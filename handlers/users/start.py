from aiogram import types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    InlineQueryResultPhoto, ReplyKeyboardMarkup, KeyboardButton

from handlers.users.checkPhone import check_phone_number
from handlers.users.checkSubscription import is_user_subscribed, check_subscription
from loader import dp, db, bot

JOIN_PHOTO = "https://t.me/MyUzBots/251"
PHOTO_URL = "https://t.me/MyUzBots/251"
REQUIRED_COUNT = 10
VALID_PREFIXES = {
    "33", "50", "55", "70", "71", "72", "73", "74", "75",
    "77", "78", "79", "88", "90", "91", "93", "94", "95", "97", "98", "99"
}

JOIN_TEXT = f"""🎄 YANGI YIL OLIMPIADASI 🎄
Ingliz tilidan bilimlaringizni sinab ko'ring va sovrinlarni qo'lga kiriting! 😊

🎁 Sovrinlar:
🥇 1-o'rin: 300 000 so'm + sertifikat
🥈 2-o'rin: 200 000 so'm + sertifikat
🥉 3-5-o'rin: 100 000 so'm + sertifikat

👉 Ishtirok etish uchun kanallarimizga obuna bo‘ling va bilimlaringizni sinang! 🏆"""


async def start_text(user_id):
    START_TEXT = f"""🎄YANGI YIL OLIMPIADASI! Ingliz tilidan bilimlaringizni sinab ko'ring va pul yutuqlarini qo'lga kiriting.
    
🏆 YUTUQLAR:
🥇 1-o'rin: 300 ming so'm va sertifikat
🥈 2-o'rin: 200 ming so'm va sertifikat
🥉 3-o'rin: 100 ming so'm va sertifikat
🏅 4-o'rin: 100 ming so'm va sertifikat
🏅 5-o'rin: 100 ming so'm va sertifikat

🫵 BU YUTUQLARNI SIZ HAM QO'LGA KIRITA OLASIZ! 🫵
👇 Kirish uchun bosing 👇
🔗 https://t.me/UzOlimpiada_Bot?start={user_id}"""

    return START_TEXT


@dp.callback_query_handler(lambda c: c.data == 'check_subscription')
async def process_callback_check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # 1. Tekshirish: foydalanuvchi barcha kanallarga obuna bo‘lganmi?
    if not await is_user_subscribed(user_id):
        await bot.answer_callback_query(
            callback_query.id,
            text="❌ Siz barcha kerakli kanallarga obuna bo‘lmagansiz. Iltimos, obuna bo‘ling.",
            show_alert=True
        )
        return
    await bot.answer_callback_query(callback_query.id, text="✅ Obuna tasdiqlandi!")
    await callback_query.message.delete()

    user_info = await db.select_info(str(user_id))
    referral_id = user_info.get('refferal')

    if referral_id:
        referral_info = await db.select_info(str(referral_id))
        referral_count = referral_info['count'] + 1

        await db.add_count(str(referral_id))
        await db.add_player(str(referral_id), referral_info['username'], referral_info['phone'])

        try:
            await bot.send_message(
                int(referral_id),
                f"🎉 Siz taklif qilgan do‘stingiz {callback_query.from_user.first_name} kanallarimizga obuna bo‘ldi!\n"
                f"✅ Sizga +1 ball berildi. Umumiy ballar: {referral_count}"
            )
        except:
            pass

    if not user_info['phone']:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))

        await callback_query.message.answer(
            "📱 Telefon raqamingizni yozib yuboring.\n\nMasalan: +998901234567\n\n"
            "Yoki quyidagi tugmani bosing:",
            reply_markup=keyboard
        )
        await db.mark_phone(user_id)  # belgilab qo‘yasizki: telefon raqam kutilmoqda
        await bot.answer_callback_query(callback_query.id, text="✅ Obuna tasdiqlandi. Endi raqamingizni yuboring!")
        return


    await callback_query.message.answer_photo(
        PHOTO_URL,
        caption=await start_text(user_id),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton("🏆 QATNASHISH ✅", url=f"https://t.me/UzOlimpiada_Bot?start={user_id}")
        ]]),
        parse_mode="HTML"
    )
    await callback_query.message.answer(
        f"👆 Yuqoridagi habarni do‘stlaringizga yuboring.\n\n"
        f"Sizdagi ballar soni: {user_info['count']} ball\n\n"
        f"- {REQUIRED_COUNT} ball yig‘ganingizda yopiq kanalga kirish imkoniga ega bo‘lasiz ✅",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton("🔗 Do‘stlarga yuborish", switch_inline_query="share")
        ]]),
        parse_mode="HTML"
    )



@dp.message_handler()
async def bot_start(message: types.Message):
    referral_id = message.get_args()
    user_id = str(message.from_user.id)

    user_data = {
        'telegram_id': user_id,
        'status': True,
        'username': message.from_user.username,
    }

    try:
        if referral_id and referral_id != user_id:
            referred_user = await db.select_info(str(referral_id))
            if referred_user:
                user_data['refferal'] = str(referral_id)
                try:
                    await bot.send_message(
                        int(referral_id),
                        f"Siz do‘stingiz {message.from_user.first_name} ni botga taklif qildingiz. "
                        "Agar u kanallarimizga obuna bo‘lsa va telefon raqamini yuborsa, sizga 1 ball beriladi."
                    )
                except:
                    pass
        await db.add(table_name='users', fields=user_data)
    except Exception as e:
        print(f"Error saving user: {e}")

    if not await check_subscription(message):
        return

    if not await check_phone_number(message):
        return

    # 4. If both passed, show welcome & share
    referral_info = await db.select_info(user_id)
    referral_count = referral_info['count']

    await message.answer_photo(
        PHOTO_URL,
        caption=await start_text(message.from_user.id),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="🏆 QATNASHISH ✅",
                    url=f"https://t.me/UzOlimpiada_Bot?start={message.from_user.id}"
                )
            ]]
        ),
        parse_mode="HTML"
    )

    await message.answer(
        f"👆 Yuqoridagi habarni do'stlaringizga va guruhlarga yuboring.\n\n"
        f"📊 Sizdagi ballar soni: {referral_count} ball\n\n"
        f"🎯 {REQUIRED_COUNT} ball yig'sangiz yutuqli testlar o'tkaziladigan yopiq kanalga ulanish imkonini olasiz ✅",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="🔗 Do‘stlarga yuborish",
                    switch_inline_query="share"
                )
            ]]
        ),
        parse_mode="HTML"
    )



@dp.inline_handler(state="*")
async def inline_share(query: types.InlineQuery):
    if query.query == "ads":
        await handle_ads_query(query)
    else:
        await handle_share_query(query)

async def handle_share_query(query: types.InlineQuery):
    text =  f"""🎄YANGI YIL OLIMPIADASI! Ingliz tilidan bilimlaringizni sinab ko'ring va pul yutuqlarini qo'lga kiriting.
    
🏆 YUTUQLAR:
🥇 1-o'rin: 300 ming so'm va sertifikat
🥈 2-o'rin: 200 ming so'm va sertifikat
🥉 3-o'rin: 100 ming so'm va sertifikat
🏅 4-o'rin: 100 ming so'm va sertifikat
🏅 5-o'rin: 100 ming so'm va sertifikat

🫵 BU YUTUQLARNI SIZ HAM QO'LGA KIRITA OLASIZ! 🫵
<a href='https://t.me/UzOlimpiada_Bot?start={query.from_user.id}'>👉 Kirish uchun bosing 👈</a>"""
    await query.answer(
        results=[
            InlineQueryResultPhoto(
                photo_url=PHOTO_URL,
                id=f"share",
                title="👉 Ulashish uchun bosing",
                description="Share to your friend",
                caption=text,
                thumb_url="https://static.vecteezy.com/system/resources/previews/012/689/054/non_2x/share-icon-3d-illustration-vector.jpg",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🏆 QATNASHISH ✅",
                                url=f"https://t.me/UzOlimpiada_Bot?start={query.from_user.id}"
                            )
                        ]
                    ]
                )
            )
        ],
        cache_time=1
    )


async def handle_ads_query(query: types.InlineQuery):
    text =  f"""🎄YANGI YIL OLIMPIADASI! Ingliz tilidan bilimlaringizni sinab ko'ring va pul yutuqlarini qo'lga kiriting.
    
🏆 YUTUQLAR:
🥇 1-o'rin: 300 ming so'm va sertifikat
🥈 2-o'rin: 200 ming so'm va sertifikat
🥉 3-o'rin: 100 ming so'm va sertifikat
🏅 4-o'rin: 100 ming so'm va sertifikat
🏅 5-o'rin: 100 ming so'm va sertifikat

🫵 BU YUTUQLARNI SIZ HAM QO'LGA KIRITA OLASIZ! 🫵
<a href='https://t.me/UzOlimpiada_Bot?start='>👉 Kirish uchun bosing 👈</a>"""
    await query.answer(
        results=[
            InlineQueryResultPhoto(
                photo_url=PHOTO_URL,
                id=f"ads",
                title=f"Share to your friend",
                description="🔗 Ulashish uchun bosing",
                caption=text,
                thumb_url="https://static.vecteezy.com/system/resources/previews/012/689/054/non_2x/share-icon-3d-illustration-vector.jpg",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🏆 QATNASHISH ✅",
                                url=f"https://t.me/UzOlimpiada_Bot?start="
                            )
                        ]
                    ]
                )
            )
        ],
        cache_time=1
    )



