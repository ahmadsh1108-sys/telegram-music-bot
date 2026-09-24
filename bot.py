import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@shegeftiha_iran_jahan"
CHANNEL_URL = "https://t.me/shegeftiha_iran_jahan"

favorites = {}

async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            await update.message.reply_text(
                "❌ برای استفاده از ربات باید در کانال ما عضو بشید.\n\n📢 لینک عضویت: " + CHANNEL_URL
            )
            return False
    except Exception as e:
        await update.message.reply_text("⚠️ خطا در بررسی عضویت. مطمئن شو ربات ادمین کانال است.")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return
    await update.message.reply_text(
        "🎵 سلام! به MelodyHunter خوش اومدی.\n\n"
        "برای جستجوی آهنگ، فقط اسمش رو بنویس.\n"
        "برای دیدن راهنما، دستور /help رو بزن."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return
    await update.message.reply_text(
        "📖 راهنمای ربات MelodyHunter\n\n"
        "🔍 جستجوی آهنگ خارجی:\n"
        "فقط اسم آهنگ یا خواننده رو بنویس (مثلاً: Ed Sheeran)\n\n"
        "👤 جستجوی خواننده خارجی:\n"
        "دستور /artist و بعد اسم خواننده\n"
        "مثال: /artist Ed Sheeran\n\n"
        "🇮🇷 جستجوی آهنگ ایرانی:\n"
        "دستور /iran و بعد اسم خواننده یا آهنگ\n"
        "مثال: /iran شادمهر\n\n"
        "⭐ ذخیره آهنگ:\n"
        "روی دکمه ⭐ ذخیره بزن تا آهنگ به لیست علاقه‌مندی‌هات اضافه بشه\n\n"
        "📤 اشتراک‌گذاری:\n"
        "روی دکمه 📤 بزن تا لینک آهنگ رو ببینی\n\n"
        "🎵 پیشنهاد مشابه:\n"
        "روی دکمه 🎵 مشابه بزن تا آهنگ‌های مشابه ببینی\n\n"
        "❤️ آهنگ‌های موردعلاقه:\n"
        "دستور /favorites برای دیدن لیست ذخیره شده‌ها"
    )

async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return
    user_id = update.effective_user.id
    if user_id not in favorites or not favorites[user_id]:
        await update.message.reply_text("❌ هنوز هیچ آهنگی ذخیره نکردی.")
        return

    await update.message.reply_text("⭐ آهنگ‌های موردعلاقه‌ت:")
    for fav in favorites[user_id]:
        message = f"🎵 {fav['title']}\n👤 خواننده: {fav['artist']}"
        buttons = []
        if fav.get('preview'):
            buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=fav['preview'])])
        if fav.get('link'):
            buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=fav['link'])])
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        await update.message.reply_text(message, reply_markup=reply_markup)

async def send_song_with_buttons(update, track, artist_name):
    title = track['title']
    preview = track.get('preview', '')
    link = track.get('link', '')

    message = f"🎵 {title}\n👤 خواننده: {artist_name}\n"

    buttons = []
    if preview:
        buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=preview)])
    if link:
        buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=link)])
        buttons.append([InlineKeyboardButton("⭐ ذخیره", callback_data=f"fav|{title}|{artist_name}")])
        buttons.append([InlineKeyboardButton("📤 اشتراک‌گذاری", callback_data=f"share|{link}")])
        buttons.append([InlineKeyboardButton("🎵 مشابه", callback_data=f"similar|{title}|{artist_name}")])

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text(message, reply_markup=reply_markup)

async def artist_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return

    if not context.args:
        await update.message.reply_text("❌ لطفاً اسم خواننده رو هم بنویس.\nمثال: /artist Ed Sheeran")
        return

    artist_name = " ".join(context.args)
    await update.message.reply_text(f"🔍 در حال جستجوی آهنگ‌های {artist_name} ...")

    try:
        url = f"https://api.deezer.com/search/artist?q={artist_name}&limit=1"
        response = requests.get(url)
        data = response.json()

        if not data.get('data'):
            await update.message.reply_text("❌ خواننده‌ای با این اسم پیدا نشد.")
            return

        artist_id = data['data'][0]['id']
        artist_real_name = data['data'][0]['name']

        tracks_url = f"https://api.deezer.com/artist/{artist_id}/top?limit=5"
        tracks_response = requests.get(tracks_url)
        tracks_data = tracks_response.json()

        if not tracks_data.get('data'):
            await update.message.reply_text("❌ آهنگی از این خواننده پیدا نشد.")
            return

        await update.message.reply_text(f"🎵 آهنگ‌های برتر {artist_real_name}:")

        for track in tracks_data['data']:
            await send_song_with_buttons(update, track, artist_real_name)

    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

async def iran_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جستجوی آهنگ‌های ایرانی از طریق API ماجید"""
    if not await is_user_member(update, context):
        return

    if not context.args:
        await update.message.reply_text("❌ لطفاً اسم خواننده یا آهنگ رو بنویس.\nمثال: /iran شادمهر")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🇮🇷 در حال جستجوی {query} ...")

    try:
        search_url = f"https://api.majidapi.ir/music/radiojavan?action=search&s={query}"
        response = requests.get(search_url, timeout=15)
        data = response.json()

        if not data or 'result' not in data or not data['result']:
            await update.message.reply_text("❌ متأسفانه آهنگ ایرانی پیدا نشد. یه اسم دیگه امتحان کن.")
            return

        await update.message.reply_text(f"🎵 نتایج جستجو برای {query}:")

        for song in data['result'][:5]:
            title = song.get('title', 'ناشناس')
            artist = song.get('artist', 'ناشناس')
            song_id = song.get('id', '')

            link = f"https://play.radiojavan.com/song/{song_id}" if song_id else ""

            message = f"🎵 {title}\n👤 خواننده: {artist}\n"
            buttons = []
            if link:
                buttons.append([InlineKeyboardButton("🔗 صفحه آهنگ", url=link)])

            reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
            await update.message.reply_text(message, reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجوی ایرانی. لطفاً بعداً امتحان کن.")
        print(f"Iran Search Error: {e}")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return

    query = update.message.text
    await update.message.reply_text(f"🔍 در حال جستجو برای: {query} ...")

    try:
        url = f"https://api.deezer.com/search?q={query}&limit=5"
        response = requests.get(url)
        data = response.json()

        if not data.get('data'):
            await update.message.reply_text("❌ متأسفانه آهنگی پیدا نشد. یه اسم دیگه امتحان کن.")
            return

        for track in data['data']:
            await send_song_with_buttons(update, track, track['artist']['name'])

    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("fav|"):
        parts = data.split("|")
        title = parts[1]
        artist = parts[2]
        user_id = update.effective_user.id

        if user_id not in favorites:
            favorites[user_id] = []

        favorites[user_id].append({
            'title': title,
            'artist': artist,
            'preview': '',
            'link': ''
        })

        await query.edit_message_text(f"⭐ آهنگ {title} از {artist} ذخیره شد!")

    elif data.startswith("share|"):
        link = data.replace("share|", "")
        share_text = f"🎵 این آهنگ رو از MelodyHunter پیدا کردم:\n{link}"
        await query.edit_message_text(f"📤 متن اشتراک‌گذاری:\n\n{share_text}")

    elif data.startswith("similar|"):
        parts = data.split("|")
        title = parts[1]
        artist = parts[2]
        await query.edit_message_text(f"🔍 آهنگ‌های مشابه با {title} از {artist} ...")

        try:
            url = f"https://api.deezer.com/search?q={artist}&limit=5"
            response = requests.get(url)
            data_json = response.json()

            if data_json.get('data'):
                for track in data_json['data']:
                    similar_title = track['title']
                    similar_artist = track['artist']['name']
                    preview = track.get('preview', '')
                    link = track.get('link', '')

                    message = f"🎵 {similar_title}\n👤 خواننده: {similar_artist}\n"
                    buttons = []
                    if preview:
                        buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=preview)])
                    if link:
                        buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=link)])

                    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
                    await query.message.reply_text(message, reply_markup=reply_markup)
        except Exception as e:
            print(f"Similar Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("artist", artist_search))
    application.add_handler(CommandHandler("iran", iran_search))
    application.add_handler(CommandHandler("favorites", favorites_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("Bot is running...")
    application.run_polling()
