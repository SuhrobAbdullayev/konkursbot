from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from filters import IsSuperAdmin
from keyboards.inline.superAdminKeyboards import menu_super_admin
from loader import dp


@dp.message_handler(IsSuperAdmin(), CommandStart(), state="*")
async def user_bot_start(message: types.Message):
    await message.answer(f"Salom Katta Admin, {message.from_user.full_name}!", reply_markup=menu_super_admin)


@dp.callback_query_handler(IsSuperAdmin(), text_contains="superadmin:cancel", state="*")
async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.edit_text("Bekor qilindi!", reply_markup=menu_super_admin)

    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
    except KeyError:
        pass
