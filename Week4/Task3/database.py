import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "classicmodels"),
    "user": os.getenv("DB_USER", "ayamkattel"),
    "password": os.getenv("DB_PASSWORD", ""),
}

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(**DB_CONFIG)
    return _pool


async def execute_query(sql: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql)
        return [dict(row) for row in rows]


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None