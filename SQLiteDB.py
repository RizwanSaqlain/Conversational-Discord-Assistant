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


async def init_classroom_db():
    # Connect to the separate database file for Google Classroom data.
    async with aiosqlite.connect('classroom.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                courseId VARCHAR(20),
                announcementId VARCHAR(20),
                text TEXT,
                materials JSON,
                state VARCHAR(20),
                alternateLink TEXT,
                creationTime DATETIME,
                updateTime DATETIME,
                creatorUserId VARCHAR(30),
                PRIMARY KEY (courseId, announcementId)
            )
        ''')
        await db.commit()


async def init_courseworks_db():
    # Connect to the Google Classroom database file.
    async with aiosqlite.connect('classroom.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS courseWorks (
                courseId VARCHAR(20),
                courseWorkId VARCHAR(20),
                title TEXT,
                state VARCHAR(20),
                alternateLink TEXT,
                creationTime DATETIME,
                updateTime DATETIME,
                maxPoints INTEGER,
                workType TEXT,
                submissionModificationMode TEXT,
                creatorUserId VARCHAR(30),
                PRIMARY KEY (courseId, courseWorkId)
            )
        ''')
        await db.commit()


async def init_courseworkmaterials_db():
    # Connect to the Google Classroom database file.
    async with aiosqlite.connect('classroom.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS courseWorkMaterials (
                courseId VARCHAR(20),
                courseWorkMaterialId VARCHAR(20),
                title TEXT,
                description TEXT,
                materials JSON,
                state VARCHAR(20),
                alternateLink TEXT,
                creationTime DATETIME,
                updateTime DATETIME,
                creatorUserId VARCHAR(30),
                PRIMARY KEY (courseId, courseWorkMaterialId)
            )
        ''')
        await db.commit()



async def insert_data_announcement(announcement):
    courseId = announcement['courseId']
    announcementId = announcement['id']
    text = announcement['text']
    state = announcement['state']
    alternateLink = announcement['alternateLink']
    creationTime = format_datetime(announcement['creationTime'])
    updateTime = format_datetime(announcement['updateTime'])
    creatorUserId = announcement['creatorUserId']
    materials = None

    # If there are materials, process them (this example stores the last driveFile found)
    try:
        if 'materials' in announcement:
            for material in announcement['materials']:
                # This example assumes each material has a 'driveFile' key.
                drive_file = material.get('driveFile')
                if drive_file:
                    materials = json.dumps(drive_file)
    except KeyError:
        pass

    query = """
        INSERT INTO announcements 
        (courseId, announcementId, text, materials, state, alternateLink, creationTime, updateTime, creatorUserId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    async with aiosqlite.connect('classroom.db') as db:
        await db.execute(query, (
            courseId, 
            announcementId, 
            text, 
            materials, 
            state, 
            alternateLink, 
            creationTime, 
            updateTime, 
            creatorUserId
        ))
        await db.commit()

# Example usage:
# asyncio.run(insert_data_announcement(announcement_data))






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
asyncio.run(init_classroom_db())
asyncio.run(init_courseworks_db())
asyncio.run(init_courseworkmaterials_db())