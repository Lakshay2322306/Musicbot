import os
import re
from telebot import TeleBot
from yt_dlp import YoutubeDL

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN environment variable is not set!")

bot = TeleBot(BOT_TOKEN)

# Function to sanitize filenames
def sanitize_filename(name):
    # Remove invalid characters for file systems
    return re.sub(r'[\\/*?:"<>|]', "", name)

# yt-dlp options with cookies file for authentication
ydl_opts = {
    'format': 'bestaudio/best',  # Best available audio format
    'outtmpl': '%(title)s.%(ext)s',  # Filename template
    'cookiefile': 'cookies.txt',  # Use the cookies file
}

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🎵 Welcome to the Music Bot! 🎵\n"
        "Send me the name of a song, and I'll fetch it for you!"
    )

# Song download handler
@bot.message_handler(func=lambda message: True)
def download_song(message):
    song_name = message.text.strip()
    bot.reply_to(message, f"🔍 Searching for '{song_name}', please wait...")

    try:
        # Download the song using yt-dlp
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            file_path = ydl.prepare_filename(info['entries'][0])
            sanitized_path = sanitize_filename(file_path)

            # Rename file if needed
            if file_path != sanitized_path:
                os.rename(file_path, sanitized_path)
            file_path = sanitized_path

        # Ensure the file exists before sending
        if not os.path.exists(file_path):
            bot.reply_to(message, "⚠️ Unable to locate the downloaded file. The download might have failed.")
            return

        # Send the downloaded file
        with open(file_path, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file)

        # Clean up the file
        os.remove(file_path)

    except Exception as e:
        bot.reply_to(message, f"⚠️ An error occurred: {e}")

# Start the bot polling
if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.polling()
