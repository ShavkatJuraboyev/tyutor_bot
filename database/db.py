import aiosqlite
import os

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "bot.db")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# ==========================
# Database Initialization   
# ==========================
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT
            )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS start_page (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            photo_id TEXT,
            caption TEXT
        )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS tutors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                name TEXT,
                subject TEXT,
                contact_info TEXT
            )
            """)
        
        await db.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            invite_link TEXT
        )
        """)

        await db.commit()

# ==========================
# User Operations
# ==========================
async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username, full_name, ))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM users
        """)
        users = await cursor.fetchall()
        return users

async def get_user_one(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM users WHERE user_id = ?
        """, (user_id,))
        user = await cursor.fetchone()
        return user

async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM users WHERE user_id = ?
        """, (user_id,))
        await db.commit()


#===========================
# Start Page Operations
#===========================
async def set_start_page(photo_id: str, caption: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO start_page (id, photo_id, caption)
            VALUES (1, ?, ?)
        """, (photo_id, caption,))
        await db.commit()

async def get_start_page():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM start_page WHERE id = 1
        """)
        start_page = await cursor.fetchone()
        return start_page

async def update_start_page(photo_id: str, caption: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE start_page
            SET photo_id = ?, caption = ?
            WHERE id = 1
        """, (photo_id, caption,))
        await db.commit()

async def delete_start_page():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM start_page WHERE id = 1
        """)
        await db.commit()

# ==========================
# Tutor Operations
# ==========================
async def add_tutor(user_id: int, name: str, subject: str, contact_info: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO tutors (user_id, name, subject, contact_info)
            VALUES (?,?, ?, ?)
        """, (user_id, name, subject, contact_info,))
        await db.commit()

async def get_all_tutors():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM tutors
        """)
        tutors = await cursor.fetchall()
        return tutors

async def get_tutor_one(tutor_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM tutors WHERE id = ?
        """, (tutor_id,))
        tutor = await cursor.fetchone()
        return tutor

async def update_tutor(tutor_id: int, user_id: int, name: str, subject: str, contact_info: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE tutors
            SET user_id = ?, name = ?, subject = ?, contact_info = ?
            WHERE id = ?
        """, (user_id, name, subject, contact_info, tutor_id,))
        await db.commit()

async def delete_tutor(tutor_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM tutors WHERE id = ?
        """, (tutor_id,))
        await db.commit()

# ==========================
# Channel Operations
# ==========================
async def add_channel(title: str, invite_link: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO channels (title, invite_link)
            VALUES (?, ?)
        """, (title, invite_link,))
        await db.commit()

async def get_all_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM channels
        """)
        channels = await cursor.fetchall()
        return channels

async def update_channel(channel_id: int, title: str, invite_link: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE channels
            SET title = ?, invite_link = ?
            WHERE id = ?
        """, (title, invite_link, channel_id,))
        await db.commit()

async def delete_channel(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM channels WHERE id = ?
        """, (channel_id,))
        await db.commit()

async def get_channel_one(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM channels WHERE id = ?
        """, (channel_id,))
        channel = await cursor.fetchone()
        return channel