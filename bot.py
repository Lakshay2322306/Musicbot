import os
import random
from telebot import TeleBot
from yt_dlp import YoutubeDL

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN environment variable is not set!")

bot = TeleBot(BOT_TOKEN)

# Load proxies from a file
def get_proxies():
    with open("proxies.txt", "r") as file:
        return [proxy.strip() for proxy in file.readlines()]

# yt-dlp options with proxy support
def get_ydl_opts(proxy):
    return {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'proxy': f"http://{proxy}",  # Add proxy to yt-dlp options
    }

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎵 Welcome to the Music Bot! 🎵")

@bot.message_handler(func=lambda message: True)
def download_song(message):
    song_name = message.text.strip()
    bot.reply_to(message, f"🔍 Searching for '{song_name}'...")
    proxies = get_proxies()
    for proxy in proxies:
        try:
            print(f"Trying proxy: {proxy}")
            ydl_opts = get_ydl_opts(proxy)
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
                file_path = ydl.prepare_filename(info['entries'][0])

            with open(file_path, 'rb') as audio_file:
                bot.send_audio(message.chat.id, audio_file)
            os.remove(file_path)
            return  # Exit if successful
        except Exception as e:
            print(f"Proxy failed: {proxy}. Error: {e}")
            continue
    bot.reply_to(message, "⚠️ All proxies failed. Please try again later.")

if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.polling()
