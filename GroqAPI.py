import os
import asyncio
from groq import Groq


def _sync_query_llm(prompt: str) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """
                You are an AI assistant for a Discord group. You can:
                - Fetch weather data with `!weather <city>`. Default city is New Delhi.
                
                Rules: 
                Response must start with the command when using the command in the above given syntax. Data will be sent in next response.
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

async def query_llm(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, _sync_query_llm, prompt)
    return response
