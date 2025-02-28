import asyncio
import aiosqlite
import json
from datetime import datetime

def format_datetime(datetime_str):
    datetimeObject = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_datetime_str = datetimeObject.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_datetime_str

async def init_db():
    async with aiosqlite.connect('chatbot.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()



async def save_message(discord_user_id, role, message):
    async with aiosqlite.connect('chatbot.db') as db:
        await db.execute(
            "INSERT INTO messages (discord_user_id, role, message) VALUES (?, ?, ?)",
            (discord_user_id, role, message)
        )
        await db.commit()

async def get_recent_messages(discord_user_id, limit=10):
    async with aiosqlite.connect('chatbot.db') as db:
        cursor = await db.execute(
            "SELECT role, message FROM messages WHERE discord_user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (discord_user_id, limit)
        )
        rows = await cursor.fetchall()
        # Reverse to have the conversation in chronological order
        return list(reversed(rows))


async def clear_history(discord_user_id: str):
    async with aiosqlite.connect('chatbot.db') as db:
        await db.execute(
            "DELETE FROM messages WHERE discord_user_id = ?",
            (discord_user_id,)
        )
        await db.commit()

async def clear_all_history_and_reset():
    async with aiosqlite.connect('chatbot.db') as db:
        # Delete all rows
        await db.execute("DELETE FROM messages")
        # Reset the autoincrement counter
        await db.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
        await db.commit()
        
asyncio.run(init_db())
