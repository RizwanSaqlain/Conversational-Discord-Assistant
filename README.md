# Discord Chatbot

## Project Overview
This project is a Discord bot that interacts with users and provides functionalities such as fetching weather data and managing conversation history.

## Key Components
1. **GroqAPI.py**: 
   - Contains functions to interact with the Groq API, allowing the bot to generate responses based on user prompts.
   - Includes synchronous and asynchronous functions for querying the API.

2. **main.py**: 
   - Serves as the core of the Discord bot, handling commands like `!weather`, `!chat`, and `!clear`.
   - Manages user interactions and saves messages to a database.

3. **weatherAPI.py**: 
   - Responsible for fetching current weather reports for a specified city.
   - Utilizes a caching mechanism to reduce API calls.

4. **SQLiteDB.py**: 
   - Manages the database operations for saving and retrieving user messages and conversation history.

## Installation
1. Clone the repository.
2. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```

## Usage
- Start the bot by running:
  ```
  python main.py
  ```
- Use the following commands in Discord:
  - `!weather <city>`: Fetches the current weather for the specified city.
  - `!chat <message>`: Interacts with the bot using the provided message.
  - `!clear`: Clears the user's conversation history.
  - `!shutdown`: Shuts down the bot.

## Acknowledgments
- This bot uses the Groq API for generating responses.
- Weather data is fetched from the Weather API.

## License
This project is licensed under the MIT License.
