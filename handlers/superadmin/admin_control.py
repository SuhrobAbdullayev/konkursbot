import random

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, ContentTypes

from filters import IsSuperAdmin
from keyboards.inline.superAdminKeyboards import cancel, menu_super_admin
from loader import db, dp, bot


@dp.callback_query_handler(IsSuperAdmin(), text="superadmin:admins", state="*")
async def show_admins(call: CallbackQuery):
    await call.answer(cache_time=1)
    admins_list = await db.select_all_admins()
    btn = []
    for admin in admins_list:
        btn.append([InlineKeyboardButton(text=admin[1], callback_data=f"superadmin:admin:{admin[0]}")])
    btn.append([InlineKeyboardButton(text="➕ Yangi admin qo'shish", callback_data="superadmin:add_admin")])
    btn.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="superadmin:cancel")])
    await call.message.edit_text("Adminlar ro'yxati:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btn))


@dp.callback_query_handler(IsSuperAdmin(), text_contains="superadmin:add_admin", state="*")
async def add_admin(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.edit_text("Yangi admin ismini kiriting:", reply_markup=cancel)
    await state.set_state("add_admin:get_name")


@dp.message_handler(IsSuperAdmin(), state="add_admin:get_name", content_types=ContentTypes.TEXT)
async def get_admin_name(message: Message, state: FSMContext):
    await state.update_data(admin_name=message.text)
    otp = random.randint(100000, 999999)
    await message.answer("""
    Juda soz endi admin ish boshlashi uchun quydagi havolani yangi adminga forward qiling:
https://t.me/{}?start={}
""".format((await dp.bot.me).username, otp))
    await db.add_admin(name=message.text, otp=otp, telegram_id=None)


@dp.callback_query_handler(IsSuperAdmin(), text_contains="superadmin:admin:", state="*")
async def admin_control(call: CallbackQuery):
    await call.answer(cache_time=1)
    admin_id = int(call.data.split(":")[-1])
    btn = [
        [InlineKeyboardButton(text="🗑 Adminni o'chirish", callback_data=f"superadmin:delete_admin:{admin_id}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="superadmin:cancel")]
    ]
    await call.message.edit_text("Adminni boshqarish:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btn))


@dp.callback_query_handler(IsSuperAdmin(), text_contains="superadmin:delete_admin:", state="*")
async def delete_admin(call: CallbackQuery):
    await call.answer(cache_time=1)
    admin_id = int(call.data.split(":")[-1])
    await db.delete_admin(id=admin_id)
    await call.message.edit_text("Admin o'chirildi!", reply_markup=menu_super_admin)