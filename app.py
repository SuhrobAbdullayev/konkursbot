from aiogram import executor
import asyncio
from data.config import ADMINS

from handlers.superadmin.broadcast_controller import send_ads_with_task
from loader import dp, db, loop, bot
from utils.set_bot_commands import set_default_commands

async def check_ads_task():
    while True:
        users = await db.select(
            table_name="users u",
            fields="a.id as ads_id, u.id as user_id, u.telegram_id, a.chat_id, a.from_chat_id, "
                   "a.message_id, a.status",
            condition=(
                "JOIN user_ads ua ON ua.user_id = u.id "
                "JOIN ads a ON a.id = ua.ads_id "
                "WHERE a.status = TRUE ORDER BY a.created_at LIMIT 200"
            )
        )

        left_users_count = await db.select(table_name="user_ads", fields="*")

        if len(left_users_count) != 0:
            await bot.send_message(chat_id=ADMINS[0], text=f"Keyngi 200 ta userga xabar yuborilmoqda...\n Qoldi: {len(left_users_count)}")

            status = await send_ads_with_task(users=users)

            if status:
                await bot.send_message(chat_id=ADMINS[0], text="✅ xabar 200 kishiga yuborildi")
                await asyncio.sleep(60)
                await check_ads_task()
        else:
            await asyncio.sleep(120)


async def on_startup(dispatcher):
    await db.create()

    await db.create_table(table_name='users', fields="""
                id SERIAL PRIMARY KEY,
                telegram_id VARCHAR(255) NOT NULL UNIQUE,
                status BOOLEAN NOT NULL DEFAULT TRUE,
                username VARCHAR(255) NULL,
                refferal VARCHAR(255) NULL,
                count INTEGER NOT NULL DEFAULT 0,
                is_join BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            """)


    await db.create_table(table_name='ads', fields="""
                id SERIAL PRIMARY KEY,
                chat_id VARCHAR(255) NOT NULL,
                from_chat_id VARCHAR(255) NOT NULL,
                message_id VARCHAR(255) NOT NULL,
                status BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
        """)

    await db.create_table(table_name='channels', fields="""
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                telegram_id VARCHAR(255) NOT NULL UNIQUE,
                invite_link VARCHAR(255) NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            """)

    await db.create_table(table_name='players', fields="""
                id SERIAL PRIMARY KEY,
                telegram_id VARCHAR(255) NOT NULL UNIQUE
            """)

    await db.create_table(table_name='user_ads', fields="""
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                ads_id INTEGER NOT NULL,
                UNIQUE (user_id, ads_id),
                FOREIGN KEY (user_id) REFERENCES users (id)
                ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ads_id) REFERENCES ads (id)
                ON DELETE CASCADE ON UPDATE CASCADE
        """)

    # await set_default_commands(dispatcher)

    loop.create_task(check_ads_task())

    await set_default_commands(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
