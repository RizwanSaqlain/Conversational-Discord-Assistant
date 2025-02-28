import time
from SQLiteDB import save_message, get_recent_messages, clear_history
from GroqAPI import  query_llm 
from weatherAPI import get_currentWeatherReports
import discord
import os

intents = discord.Intents.all()
intents.members = True
intents.messages = True

bot = discord.Client(intents=intents)
bot_token = os.environ.get("DISCORD_BOT_TOKEN")

last_user_id = None

def split_message(message: str, chunk_size: int = 2000):
    """
    Split a long message into chunks of a given maximum size.
    """
    return [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    global last_user_id
    # Ignore messages from the bot itself
    # if message.author == bot.user:
    #     return
    if message.content == '!shutdown':
        await message.channel.send("Shutting down")
        time.sleep(2)
        print("shutdown")
        await bot.close()    
        
    if message.content.startswith("!weather"):
            
        city = message.content[len("!weather"):].strip()
        data = get_currentWeatherReports(city)
        embed = discord.Embed(title="Weather Report", description="Weather details here", color=0x00ff
        )
        embed.add_field(name="Location", value=f"{data['location']['name']}, {data['location']['region']}, {data['location']['country']}", inline=False)
        embed.add_field(name="Temperature", value=f"{data['current']['temp_c']}°C / {data['current']['temp_f']}°F", inline=True)
        embed.add_field(name="Condition", value=data['current']['condition']['text'], inline=True)
        embed.add_field(name="Humidity", value=f"{data['current']['humidity']}%", inline=True)
        embed.add_field(name="Wind", value=f"{data['current']['wind_kph']} kph / {data['current']['wind_mph']} mph", inline=True)
        embed.add_field(name="Pressure", value=f"{data['current']['pressure_mb']} mb / {data['current']['pressure_in']} in", inline=True) 
        if message.author == bot.user:
            await save_message(last_user_id, "WeatherAPI", str(data))
        await message.channel.send(embed=embed)

    if message.content.startswith("!clear"):
        discord_user_id = str(message.author.id)
        await clear_history(discord_user_id)
        await message.channel.send("Your conversation history has been cleared.")

    if message.content.startswith("!chat"):
        user_query = message.content[len("!chat"):].strip()
        if not user_query:
            await message.channel.send("Please provide a message after !chat.")
            return
        discord_user_id = str(message.author.id)
        
        # Save the user's message to the database
        await save_message(discord_user_id, "user", user_query)

        # Retrieve the recent conversation history
        history = await get_recent_messages(discord_user_id, limit=30)

        # Build the conversation prompt from history
        conversation_prompt = ""
        for role, msg in history:
            conversation_prompt += f"{role}: {msg}\n"
        conversation_prompt += "assistant: "
        print(conversation_prompt)
        # Query the Groq API for a response
        response_text = await query_llm(conversation_prompt)

        # Save the assistant's response to the database
        await save_message(discord_user_id, "assistant", response_text)
        last_user_id = discord_user_id
        # Check if the response exceeds Discord's 2000 character limit
        if len(response_text) > 2000:
            chunks = split_message(response_text)
            for chunk in chunks:
                await message.channel.send(chunk)
        else:
            await message.channel.send(response_text)

bot.run(bot_token)
