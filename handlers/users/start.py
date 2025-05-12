from aiogram import types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
from loader import dp, db, bot

CLOSED_URL = "https://t.me/+eEdKajl3yO44Njli"
JOIN_PHOTO = "https://t.me/MyUzBots/251"
PHOTO_URL = "https://t.me/MyUzBots/251"
REQUIRED_COUNT = 10
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

async def is_user_subscribed(user_id: int) -> bool:
    get_channels = await db.get_channels()
    # If there are no channels in the database, return True to bypass subscription check
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
    """
    Check subscription across multiple channels and prompt if not subscribed.
    """
    user_id = message.from_user.id
    get_channels = await db.get_channels()

    # If no channels are configured, proceed without subscription check
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

@dp.callback_query_handler(lambda c: c.data == 'check_subscription')
async def process_callback_check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_subscribed(user_id):
        user_info = await db.select_info(str(user_id))
        refferal_id = user_info['refferal']
        if not refferal_id:
            await callback_query.message.reply_photo(PHOTO_URL, await start_text(callback_query.from_user.id),
                                                     reply_markup=InlineKeyboardMarkup(
                                                         inline_keyboard=[
                                                             [
                                                                 InlineKeyboardButton(
                                                                     text="🏆 QATNASHISH ✅",
                                                                     url=f"https://t.me/UzOlimpiada_Bot?start="
                                                                 )
                                                             ]
                                                         ]
                                                     ),
                                                     parse_mode="HTML")
            await callback_query.message.answer(f"👆 Yuqoridagi habarni do'stlaringizga va guruhlarga yuboring.\n\nSizdagi ballar soni: {user_info['count']} ball \n\n- {REQUIRED_COUNT} ball yig'sangiz yutuqli testlar o'tkazib boriladigan yopiq kanalimizga ulanish imkonini qo'lga kiritasiz ✅",
                                                reply_markup=InlineKeyboardMarkup(
                                                    inline_keyboard=[
                                                        [
                                                            InlineKeyboardButton(
                                                                text="🔗 Do`stlarga yuborish",
                                                                switch_inline_query=f"share"
                                                            )
                                                        ]
                                                    ]
                                                ),
                                                parse_mode="HTML")
            await bot.answer_callback_query(callback_query.id, text="✅ Subscription confirmed!")
            await callback_query.message.delete()
        else:
            refferal_info = await db.select_info(str(refferal_id))
            refferal_count = refferal_info['count'] + 1
            if int(refferal_count) >= REQUIRED_COUNT:
                await db.add_count(str(refferal_id))
                await db.add_player(str(refferal_id))
                msg = f"⚡️ Siz taklif qilgan do`stingiz {callback_query.from_user.first_name} kanallarimizga ham azo boldi.\n\n🤩 Sizda umumiy {REQUIRED_COUNT} ball boldi va siz bizning yutuqli testlar o'tkaziladigan kanalimizga obuna bo'lishingiz mumkin ✅\n\n<strong>ID raqamingiz:</strong> <code>{refferal_id}</code>\n\n<i>👆 Bu id raqamdan testda ishtirok etish uchun foydalanasiz.</i>\n\n- Ko'proq ma'lumotlar kanalimizda berib boriladi.\n\n- Sizga omad tilaymiz 😊"
                try:
                    await bot.send_message(
                        chat_id=int(refferal_id),
                        text=msg,  # Ensure `msg` is HTML-formatted and safe
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="🔑 Kanalga qo`shilish",
                                        url=f"{CLOSED_URL}"  # Ensure CLOSED_URL is a valid URL
                                    )
                                ]
                            ]
                        )
                    )
                except: pass
            elif int(refferal_count) < REQUIRED_COUNT:
                await db.add_count(str(refferal_id))
                await db.ref_done(str(callback_query.from_user.id))
                msg = f"⚡️ Siz taklif qilgan do`stingiz {callback_query.from_user.first_name} kanallarimizga ham azo boldi va sizga +1 ball berildi. \n Sizda umumiy ballar soni {refferal_count} ta"
                try:
                    await bot.send_message(int(refferal_id), msg)
                except: pass
            await callback_query.message.reply_photo(PHOTO_URL, await start_text(callback_query.from_user.id),
                                                     reply_markup=InlineKeyboardMarkup(
                                                         inline_keyboard=[
                                                             [
                                                                 InlineKeyboardButton(
                                                                     text="🏆 QATNASHISH ✅",
                                                                     url=f"https://t.me/UzOlimpiada_Bot?start="
                                                                 )
                                                             ]
                                                         ]
                                                     ),
                                                     parse_mode="HTML")
            await callback_query.message.answer(f"👆 Yuqoridagi habarni do'stlaringizga va guruhlarga yuboring.\n\nSizdagi ballar soni: {user_info['count']} ball \n\n- {REQUIRED_COUNT} ball yig'sangiz yutuqli testlar o'tkazib boriladigan yopiq kanalimizga ulanish imkonini qo'lga kiritasiz ✅",
                                                reply_markup=InlineKeyboardMarkup(
                                                    inline_keyboard=[
                                                        [
                                                            InlineKeyboardButton(
                                                                text="🔗 Do`stlarga yuborish",
                                                                switch_inline_query=f"share"
                                                            )
                                                        ]
                                                    ]
                                                ),
                                                parse_mode="HTML")
            await bot.answer_callback_query(callback_query.id, text="✅ Subscription confirmed!")
            await callback_query.message.delete()
    else:
        await bot.answer_callback_query(callback_query.id, text="❌ You are not subscribed to all required channels. Please join them and try again.", show_alert=True)

@dp.message_handler()
async def bot_start(message: types.Message):
    refferal_id = message.get_args()
    user_data = {
        'telegram_id': str(message.from_user.id),
        'status': True,
        'username': message.from_user.username
    }
    try:
        if refferal_id:
            referred_user = await db.select_info(str(refferal_id))

            if referred_user:
                if str(refferal_id) != str(message.from_user.id):
                    user_data['refferal'] = str(refferal_id)
                    try:
                        await bot.send_message(
                            int(refferal_id),
                            f"Siz do`stingiz {message.from_user.first_name} ni botga taklif qildingiz. Agar u kanallarimizga obuna bo'lsa, sizga 1 ball beriladi."
                        )
                    except: pass

        await db.add(table_name='users', fields=user_data)
    except: pass

    if await check_subscription(message):
        refferal_info = await db.select_info(str(message.from_user.id))
        refferal_count = refferal_info['count']
        if int(refferal_count) >= REQUIRED_COUNT:
            msg = f"⚡️Siz bizning shartlarni to'liq bajargansiz. \n- Agar obuna bo'lmagan bo'lsangiz bizning yutuqli testlar o'tkaziladigan kanalimizga obuna bo'lishingiz mumkin ✅\n\n<strong>ID raqamingiz:</strong> <code>{message.from_user.id}</code>\n\n<i>👆 Bu id raqamdan testda ishtirok etish uchun foydalanasiz.</i>\n\n- Ko'proq ma'lumotlar kanalimizda berib boriladi.\n\n- Sizga omad tilaymiz 😊"
            await message.answer(
                msg,  # Ensure `msg` contains your HTML-formatted text
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🔑 Kanalga qo`shilish",
                                url=f"{CLOSED_URL}"  # Ensure CLOSED_URL is a valid URL
                            )
                        ]
                    ]
                )
            )
        elif int(refferal_count) < REQUIRED_COUNT:
            await message.answer_photo(
                PHOTO_URL,
                caption=await start_text(message.from_user.id),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🏆 QATNASHISH ✅",
                                url=f"https://t.me/UzOlimpiada_Bot?start={message.from_user.id}"
                            )
                        ]
                    ]
                ),
                parse_mode="HTML"
            )
            await message.answer(f"👆 Yuqoridagi habarni do'stlaringizga va guruhlarga yuboring.\n\nSizdagi ballar soni: {refferal_count} ball \n\n- {REQUIRED_COUNT} ball yig'sangiz yutuqli testlar o'tkazib boriladigan yopiq kanalimizga ulanish imkonini qo'lga kiritasiz ✅",
                                 reply_markup=InlineKeyboardMarkup(
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(
                                                 text="🔗 Do`stlarga yuborish",
                                                 switch_inline_query=f"share"
                                             )
                                         ]
                                     ]
                                 ),
                                 parse_mode="HTML")


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

@dp.chat_join_request_handler()
async def handle_join_request(join_request: types.ChatJoinRequest):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id

    user_info = await db.select_info(str(user_id))

    if not user_info or user_info.get("count", 0) < REQUIRED_COUNT:
        try:
            # Send a message to the user if they don't meet the criteria
            await bot.send_message(
                chat_id=user_id,
                text=("🔒 Siz bizning shartlarni to'liq bajarmagansiz. Shuning uchun yutuqli testlar o'tkaziladigan yopiq kanalimizga obuna bo'la olmaysiz 😔\n\n🔑 Shartlarni bajarish uchun /start bosing ✅"
                      ),
                parse_mode="HTML"
            )
        except: pass
        return
    await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
    await bot.send_message(
        chat_id=user_id,
        text=(
            "✅ Siz barcha shartlarni bajardingiz va yopiq kanalimizga muvaffaqiyatli qo'shildingiz!\nEndi yutuqli testlarda qatnashishingiz mumkin 🎉"
        ),
        parse_mode="HTML"
    )


