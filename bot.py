import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OMDB_TOKEN = os.environ.get("OMDB_TOKEN")
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
            keyboard = [
                [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)],
                [InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ برای استفاده از ربات باید در کانال ما عضو بشید.\n\n"
                "۱. روی دکمه «📢 عضویت در کانال» بزن\n"
                "۲. بعد از عضویت، روی دکمه «✅ عضو شدم» بزن",
                reply_markup=reply_markup
            )
            return False
    except Exception as e:
        await update.message.reply_text("⚠️ خطا در بررسی عضویت. مطمئن شو ربات ادمین کانال است.")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🔍 جستجوی آهنگ", callback_data="help_music"), InlineKeyboardButton("🎬 جستجوی فیلم", callback_data="help_movie")],
        [InlineKeyboardButton("📺 جستجوی سریال", callback_data="help_series"), InlineKeyboardButton("📖 راهنما", callback_data="help_help")],
        [InlineKeyboardButton("⭐ علاقه‌مندی‌ها", callback_data="help_fav")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🎵 سلام {user_name}! به MelodyHunter خوش اومدی 🎶\n\n"
        "من می‌تونم برات آهنگ، فیلم و سریال پیدا کنم! 🎧🎬📺\n\n"
        "🔍 چطور از من استفاده کنی:\n"
        "• برای جستجوی آهنگ: فقط اسم آهنگ یا خواننده رو بفرست\n"
        "• برای جستجوی خواننده: /artist اسم خواننده\n"
        "• برای جستجوی فیلم: /movie اسم فیلم\n"
        "• برای جستجوی سریال: /series اسم سریال\n"
        "• برای دیدن راهنما: /help\n\n"
        "🎼 منتظرت هستم، اسم آهنگ یا فیلمت رو بفرست!",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return
    await update.message.reply_text(
        "📖 راهنمای ربات MelodyHunter\n\n"
        "🎵 جستجوی آهنگ:\n"
        "فقط اسم آهنگ یا خواننده رو بنویس (مثلاً: Ed Sheeran)\n\n"
        "👤 جستجوی خواننده:\n"
        "دستور /artist و بعد اسم خواننده\n"
        "مثال: /artist Ed Sheeran\n\n"
        "🎬 جستجوی فیلم:\n"
        "دستور /movie و بعد اسم فیلم\n"
        "مثال: /movie Inception\n\n"
        "📺 جستجوی سریال:\n"
        "دستور /series و بعد اسم سریال\n"
        "مثال: /series Breaking Bad\n\n"
        "⭐ ذخیره آهنگ:\n"
        "روی دکمه ⭐ ذخیره بزن\n\n"
        "❤️ آهنگ‌های موردعلاقه:\n"
        "دستور /favorites"
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
        if fav.get('preview') and fav.get('link'):
            buttons.append([
                InlineKeyboardButton("🔊 پیش‌نمایش", url=fav['preview']),
                InlineKeyboardButton("🔗 لینک کامل", url=fav['link'])
            ])
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        await update.message.reply_text(message, reply_markup=reply_markup)

async def send_song_with_buttons(update, track, artist_name):
    title = track['title']
    preview = track.get('preview', '')
    link = track.get('link', '')

    message = f"🎵 {title}\n👤 خواننده: {artist_name}\n"

    buttons = []
    if preview and link:
        buttons.append([
            InlineKeyboardButton("🔊 پیش‌نمایش", url=preview),
            InlineKeyboardButton("🔗 لینک کامل", url=link)
        ])
    elif preview:
        buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=preview)])
    elif link:
        buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=link)])

    if link:
        buttons.append([
            InlineKeyboardButton("⭐ ذخیره", callback_data=f"fav|{title}|{artist_name}"),
            InlineKeyboardButton("📤 اشتراک‌گذاری", callback_data=f"share|{link}")
        ])

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

        tracks_url = f"https://api.deezer.com/artist/{artist_id}/top?limit=1"
        tracks_response = requests.get(tracks_url)
        tracks_data = tracks_response.json()

        if not tracks_data.get('data'):
            await update.message.reply_text("❌ آهنگی از این خواننده پیدا نشد.")
            return

        await update.message.reply_text(f"🎵 آهنگ برتر {artist_real_name}:")
        await send_song_with_buttons(update, tracks_data['data'][0], artist_real_name)

    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

async def movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return

    if not context.args:
        await update.message.reply_text("❌ لطفاً اسم فیلم رو هم بنویس.\nمثال: /movie Inception")
        return

    movie_name = " ".join(context.args)
    await update.message.reply_text(f"🎬 در حال جستجوی فیلم {movie_name} ...")

    try:
        url = "https://www.omdbapi.com/"
        params = {
            "apikey": OMDB_TOKEN,
            "t": movie_name,
            "plot": "short"
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if data.get('Response') == 'False':
            await update.message.reply_text(f"❌ فیلمی با اسم «{movie_name}» پیدا نشد.")
            return

        title = data.get('Title', 'ناشناس')
        year = data.get('Year', 'ناشناس')
        genre = data.get('Genre', 'ناشناس')
        director = data.get('Director', 'ناشناس')
        actors = data.get('Actors', 'ناشناس')
        plot = data.get('Plot', 'ناشناس')
        poster = data.get('Poster', '')
        imdb_rating = data.get('imdbRating', 'ناشناس')
        imdb_link = f"https://www.imdb.com/title/{data.get('imdbID', '')}"

        message = (
            f"🎬 {title} ({year})\n\n"
            f"🎭 ژانر: {genre}\n"
            f"🎥 کارگردان: {director}\n"
            f"👥 بازیگران: {actors}\n"
            f"⭐ امتیاز IMDb: {imdb_rating}\n\n"
            f"📝 خلاصه: {plot}\n"
        )

        buttons = [[InlineKeyboardButton("🔗 صفحه IMDb", url=imdb_link)]]
        if poster and poster != 'N/A':
            buttons.append([InlineKeyboardButton("🖼️ پوستر فیلم", url=poster)])

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(message, reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجوی فیلم. لطفاً بعداً امتحان کن.")
        print(f"Movie Error: {e}")

async def series_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return

    if not context.args:
        await update.message.reply_text("❌ لطفاً اسم سریال رو هم بنویس.\nمثال: /series Breaking Bad")
        return

    series_name = " ".join(context.args)
    await update.message.reply_text(f"📺 در حال جستجوی سریال {series_name} ...")

    try:
        url = "https://www.omdbapi.com/"
        params = {
            "apikey": OMDB_TOKEN,
            "t": series_name,
            "plot": "short"
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if data.get('Response') == 'False':
            await update.message.reply_text(f"❌ سریالی با اسم «{series_name}» پیدا نشد.")
            return

        title = data.get('Title', 'ناشناس')
        year = data.get('Year', 'ناشناس')
        genre = data.get('Genre', 'ناشناس')
        director = data.get('Director', 'ناشناس')
        actors = data.get('Actors', 'ناشناس')
        plot = data.get('Plot', 'ناشناس')
        poster = data.get('Poster', '')
        imdb_rating = data.get('imdbRating', 'ناشناس')
        total_seasons = data.get('totalSeasons', 'ناشناس')
        imdb_link = f"https://www.imdb.com/title/{data.get('imdbID', '')}"

        message = (
            f"📺 {title} ({year})\n\n"
            f"🎭 ژانر: {genre}\n"
            f"🎥 کارگردان: {director}\n"
            f"👥 بازیگران: {actors}\n"
            f"📺 تعداد فصل‌ها: {total_seasons}\n"
            f"⭐ امتیاز IMDb: {imdb_rating}\n\n"
            f"📝 خلاصه: {plot}\n"
        )

        buttons = [[InlineKeyboardButton("🔗 صفحه IMDb", url=imdb_link)]]
        if poster and poster != 'N/A':
            buttons.append([InlineKeyboardButton("🖼️ پوستر سریال", url=poster)])

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(message, reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجوی سریال. لطفاً بعداً امتحان کن.")
        print(f"Series Error: {e}")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return

    query = update.message.text
    await update.message.reply_text(f"🔍 در حال جستجو برای: {query} ...")

    try:
        url = f"https://api.deezer.com/search?q={query}&limit=1"
        response = requests.get(url)
        data = response.json()

        if not data.get('data'):
            await update.message.reply_text("❌ متأسفانه آهنگی پیدا نشد. یه اسم دیگه امتحان کن.")
            return

        track = data['data'][0]
        await send_song_with_buttons(update, track, track['artist']['name'])

    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "check_join":
        user_id = update.effective_user.id
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                await query.edit_message_text("✅ عضویت شما تأیید شد! حالا می‌تونید از ربات استفاده کنید.")
            else:
                await query.answer("❌ هنوز عضو کانال نشدی! اول عضو شو، بعد دوباره امتحان کن.", show_alert=True)
        except Exception as e:
            await query.answer("⚠️ خطا در بررسی عضویت.", show_alert=True)
        return

    if data == "help_music":
        await query.message.reply_text("🔍 برای جستجوی آهنگ، فقط اسمش رو بنویس. مثلاً: Shape of You")
    elif data == "help_help":
        await query.message.reply_text("📖 برای دیدن راهنمای کامل، دستور /help رو بزن.")
    elif data == "help_fav":
        await query.message.reply_text("⭐ برای دیدن آهنگ‌های ذخیره‌شده، دستور /favorites رو بزن.")
    elif data == "help_movie":
        await query.message.reply_text("🎬 برای جستجوی فیلم، دستور /movie و بعد اسم فیلم رو بنویس. مثلاً: /movie Inception")
    elif data == "help_series":
        await query.message.reply_text("📺 برای جستجوی سریال، دستور /series و بعد اسم سریال رو بنویس. مثلاً: /series Breaking Bad")

    elif data.startswith("fav|"):
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

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("artist", artist_search))
    application.add_handler(CommandHandler("movie", movie_search))
    application.add_handler(CommandHandler("series", series_search))
    application.add_handler(CommandHandler("favorites", favorites_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("Bot is running...")
    application.run_polling()
