from telebot import TeleBot, types
from telebot.types import Message
from telebot.util import extract_arguments
from dotenv import load_dotenv
from os import getenv, remove
from y2mate_api import first_query, second_query, third_query, appdir, Handler
import requests

load_dotenv()

handler = Handler("")
bot = TeleBot(getenv("telegram-api-token"), disable_web_page_preview=True)
file_size_limit = float(getenv("file-size-limit", 200))
cache_dir = appdir.user_cache_dir

bot_description = (
    "► **A FAST & POWERFUL TELEGRAM MUSIC  BOT WITH SOME AWESOME FEATURES.**\n\n"
    "SUPPORTED PLATFORMS:\n"
    "YouTube, SoundCloud, and more!\n\n"
    "Click on the Help button below to get information about my modules and commands.\n\n"
    "🎵 **Ready to enhance your music experience!**"
)

def create_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("ADD ME IN YOUR GROUP", url="https://t.me/YOUR_BOT_USERNAME?startgroup=true")
    )
    keyboard.add(
        types.InlineKeyboardButton("HELP & COMMANDS", callback_data="help"),
        types.InlineKeyboardButton("DEVELOPER", url="@Jukerhenapadega"),
    )
    keyboard.add(
        types.InlineKeyboardButton("SUPPORT", url="https://t.me/lakshaychats"),
        types.InlineKeyboardButton("CHANNEL", url="https://t.me/botsforfree55"),
    )
    return keyboard

def text_is_required(func):
    def decorator(message: Message):
        if not extract_arguments(message.text):
            bot.reply_to(message, "❗ Text is required!")
        else:
            try:
                bot.send_chat_action(message.chat.id, "typing")
                return func(message)
            except Exception as e:
                bot.reply_to(
                    message,
                    f"⚠️ Error occurred - {e.args[1] if e.args and len(e.args) > 1 else e}",
                )
    return decorator

def is_within_size_limit(size: str) -> bool:
    try:
        size_value = size.split(" ")[0]
        return float(size_value) <= file_size_limit if size_value.isdigit() else False
    except (IndexError, ValueError):
        return False

def make_audio_info(meta: dict) -> str:
    info = (
        f"🎵 **Title**: {meta.get('title')}\n"
        f"📺 **Channel**: {meta.get('author')}\n"
        f"📦 **Size**: {meta.get('size')}\n"
        f"🆔 **Video ID**: {meta.get('vid')}\n"
        f"⬇️ **Download**: [Click Me]({meta.get('dlink')})\n"
        f"📤 **Uploading**: {'Yes' if meta.get('download_required') else 'No'}"
    )
    return info

@bot.message_handler(commands=["start"])
def start_message(message):
    user_name = message.from_user.first_name
    greeting = f"Hello, {user_name}!\n\n"
    bot.send_message(
        message.chat.id,
        greeting + bot_description,
        parse_mode="Markdown",
        reply_markup=create_inline_keyboard(),
    )

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_callback(call):
    help_text = (
        "🎵 **Help & Commands**:\n\n"
        "🔹 Use `/audio <YouTube URL or search>` to download audio from a video.\n"
        "🔹 Use `/myid` to retrieve your Telegram ID.\n"
        "🔹 Use `/stats` (admin only) to view bot usage statistics.\n\n"
        "📦 Files under the size limit can be downloaded via Telegram.\n"
        "If the file size exceeds the limit, a download link will be provided."
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=["audio"])
@text_is_required
def download_and_send_audio_file(message: Message):
    query = extract_arguments(message.text)
    fq = first_query(query).main()
    sq = second_query(fq).main()
    third_dict = third_query(sq).main(format="mp3")
    audio_size = third_dict.get("size", "Unknown")

    download_required = is_within_size_limit(audio_size)
    third_dict["download_required"] = download_required
    third_dict["author"] = sq.raw.get("a")
    bot.send_message(
        message.chat.id,
        make_audio_info(third_dict),
        parse_mode="Markdown",
    )

    if not download_required:
        return

    try:
        saved_to = handler.save(third_dict, cache_dir, progress_bar=False, disable_history=True)
        bot.send_chat_action(message.chat.id, "upload_audio")
        bot.send_audio(
            message.chat.id,
            open(saved_to, "rb"),
            title=third_dict.get("title", "Unknown"),
            performer=sq.raw.get("a"),
        )
    except Exception as e:
        bot.reply_to(
            message,
            f"⚠️ Error occurred - {e.args[1] if e.args and len(e.args) > 1 else e}",
        )
    finally:
        try:
            remove(saved_to)
        except:
            pass

@bot.message_handler(commands=["help"])
def show_help(message: Message):
    bot.reply_to(
        message,
        "🎵 **Music Bot Help**:\n\n"
        "🔹 Use `/audio <YouTube URL>` to download audio from a video.\n"
        "🔹 Use `/myid` to retrieve your Telegram ID.\n"
        "🔹 Use `/stats` (admin only) to view bot usage statistics.\n\n"
        "📦 Files under the size limit can be downloaded via Telegram.\n"
        "If the file size exceeds the limit, a download link will be provided.",
        parse_mode="Markdown",
    )

@bot.message_handler(commands=["myid"])
def echo_user_telegram_id(message: Message):
    bot.reply_to(message, f"🆔 Your Telegram ID is: {message.from_user.id}")

@bot.message_handler(commands=["stats"])
def show_usage_statistics(message: Message):
    admin_id = int(getenv("telegram-admin-id", 0))
    if message.from_user.id == admin_id:
        bot.reply_to(
            message,
            "📊 **Bot Usage Statistics**:\n"
            f"🎵 Total audio downloads: {metadata.get('AUDIO_DOWNLOADS', 0)}\n"
            f"👥 Total users: {metadata.get('TOTAL_USERS', 0)}",
        )
    else:
        bot.reply_to(message, "❗ You are not authorized to view statistics.")

if __name__ == "__main__":
    print("🎵 Music Bot is running...")
    bot.infinity_polling(timeout=60)
