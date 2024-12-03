from telebot import TeleBot
from yt_dlp import YoutubeDL
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os

# Load the Telegram bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN environment variable is not set!")

bot = TeleBot(BOT_TOKEN)

# yt-dlp configuration for downloading public YouTube content
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '/tmp/%(title)s.%(ext)s',  # Save files temporarily
}

# Function to set up the headless Chromium driver
def setup_chromedriver():
    chrome_binary_path = "/usr/bin/chromium-browser"
    chrome_driver_path = "/usr/bin/chromedriver"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_binary_path
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    return driver

# Telegram bot handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🎵 Welcome to the Music Bot! 🎵\n"
        "Send me the name of a song, and I'll fetch it for you!"
    )

@bot.message_handler(func=lambda message: True)
def download_song(message):
    song_name = message.text.strip()
    bot.reply_to(message, f"🔍 Searching for '{song_name}', please wait...")

    try:
        # Use yt-dlp to search and download the audio
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            file_path = ydl.prepare_filename(info['entries'][0])

        # Send the downloaded file to the user
        with open(file_path, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file)

        # Clean up the temporary file
        os.remove(file_path)
    except Exception as e:
        bot.reply_to(message, f"⚠️ An error occurred: {e}")

if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.polling(none_stop=True, interval=3, timeout=20)
