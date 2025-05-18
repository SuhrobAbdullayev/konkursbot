from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result


    async def create_table(self, table_name: str, fields: str):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
        {fields}
        );
        """
        return await self.execute(sql, execute=True)


    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())


    """
    ---------------------------------------------CONTROL ADMINS--------------------------------------------------------
    """

    async def add(self, table_name: str, fields: dict):
        sql = f"""
                INSERT INTO {table_name}({', '.join(fields.keys())}) 
                VALUES({', '.join(['$' + str(i) for i in range(1, len(fields) + 1)])})
                """
        await self.execute(sql, *fields.values(), execute=True)

    async def select(self, table_name: str, fields: str = '*', condition: str = ''):
        sql = f"""
        SELECT {fields} FROM {table_name} {condition}
        """
        return await self.execute(sql, fetch=True)

    async def update(self, table_name: str, fields: dict, condition: str):
        set_fields = ', '.join([f'{key}=\'{value}\'' for key, value in fields.items()])
        sql = f"""
        UPDATE {table_name} SET {set_fields} WHERE {condition}
        """
        return await self.execute(sql, execute=True)

    async def delete(self, table_name: str, condition: str):
        sql = f"""
        DELETE FROM {table_name} WHERE {condition}
        """
        return await self.execute(sql, execute=True)

    async def add_user(self, telegram_id):
        sql = "INSERT INTO users (telegram_id) VALUES($1) returning *"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def add_player(self, telegram_id, username, phone):
        sql = "INSERT INTO players (telegram_id, username, phone) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, telegram_id, username, phone, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def delete_users(self):
        await self.execute("DELETE FROM users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE users", execute=True)

    async def select_info(self, id):
        sql = "SELECT * FROM users WHERE telegram_id = $1"
        return await self.execute(sql, id, fetchrow=True)

    async def add_count(self, id):
        sql = "UPDATE users SET count = count + 1 WHERE telegram_id = $1"
        return await self.execute(sql, id, execute=True)

    async def ref_done(self, id):
        sql = "UPDATE users SET refferal = null WHERE telegram_id = $1"
        return await self.execute(sql, id, execute=True)

    async def get_channels(self):
        sql = f"SELECT DISTINCT name, telegram_id, invite_link FROM channels"
        return await self.execute(sql, fetch=True)
    # Need ads to send
    async def need_send_ads_to_users(self, ads_id: int):
        sql = f"""
        INSERT INTO user_ads(user_id, ads_id)
        SELECT users.id, {ads_id} FROM users
        """
        return await self.execute(sql, execute=True)
