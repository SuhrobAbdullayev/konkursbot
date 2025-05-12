from loader import db


async def get_user_data(user_id, field=None):
    user_data = await db.select(table_name='users', condition=f"WHERE telegram_id = '{user_id}'")
    if not user_data:
        return None
    return user_data[0][field] if field else user_data[0]
