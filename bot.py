
import telebot
import os
from yt_dlp import YoutubeDL

# Telegram bot token from environment variables
BOT_TOKEN = os.getenv("7719494597:AAF3_TQ_HbhhbqzDRiv8vtKC1MOkxzmYOkc")
OWNER_ID = os.getenv("OWNER_ID")  # Owner's Telegram ID
OWNER_NAME = "@Jukerhenapadega"   # Owner's username
bot = telebot.TeleBot(BOT_TOKEN)

# yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(title)s.%(ext)s',
}

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        f"🎵 Welcome to the Music Bot! 🎵\n"
        f"Send me the name of a song, and I'll fetch it for you!\n"
        f"👤 Owner: {OWNER_NAME}"
    )

# Bot description command
@bot.message_handler(commands=['help', 'description'])
def bot_description(message):
    bot.reply_to(
        message,
        "📖 *Bot Description* 📖\n"
        "This bot allows you to search for and download songs by name.\n"
        f"👤 Maintained by: {OWNER_NAME}\n"
        "⚙️ Commands:\n"
        "/start - Start the bot\n"
        "/help - Get bot description\n"
        "/ping - Check bot status\n"
        "/broadcast - Send a message to all users (Owner only)",
        parse_mode="Markdown"
    )

# Ping command
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 Pong! I'm online and working!")

# Broadcast command (Owner only)
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.chat.id) == OWNER_ID:
        broadcast_message = message.text.replace("/broadcast", "").strip()
        if not broadcast_message:
            bot.reply_to(message, "📢 Please provide a message to broadcast.")
        else:
            # Fetch all chat IDs from a database or file (this part should be customized)
            # Example:
            # chat_ids = fetch_chat_ids_from_database()
            chat_ids = []  # Placeholder: Replace with actual chat IDs
            for chat_id in chat_ids:
                try:
                    bot.send_message(chat_id, f"📢 *Broadcast Message:*\n{broadcast_message}", parse_mode="Markdown")
                except Exception as e:
                    print(f"Failed to send message to {chat_id}: {e}")
            bot.reply_to(message, "✅ Broadcast sent!")
    else:
        bot.reply_to(message, "❌ You are not authorized to use this command.")

# Song download command
@bot.message_handler(func=lambda message: True)
def download_song(message):
    song_name = message.text.strip()
    bot.reply_to(message, f"🔍 Searching for '{song_name}', please wait...")

    try:
        # Search and download the song from YouTube
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            downloaded_file = ydl.prepare_filename(info['entries'][0])

        # Send the downloaded file to the user
        with open(downloaded_file, "rb") as song:
            bot.send_audio(message.chat.id, song)

        # Clean up the downloaded file
        os.remove(downloaded_file)

    except Exception as e:
        bot.reply_to(message, f"⚠️ An error occurred: {e}")

# Start polling
if __name__ == "__main__":
    bot.polling()
