import aiosqlite

DB_NAME = "users.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                usage_count INTEGER DEFAULT 0,
                subscribed INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT usage_count, subscribed FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row if row else (0, 0)

async def update_usage(user_id):
    usage, subscribed = await get_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.execute("UPDATE users SET usage_count = usage_count + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

async def reset_usage(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET usage_count = 0 WHERE user_id = ?", (user_id,))
        await db.commit()

async def set_subscribed(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.execute("UPDATE users SET subscribed = 1 WHERE user_id = ?", (user_id,))
        await db.commit()

async def is_subscribed(user_id):
    _, subscribed = await get_user(user_id)
    return bool(subscribed)

async def get_usage_count(user_id):
    usage, _ = await get_user(user_id)
    return usage
