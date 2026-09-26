import os
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

# =========================
# تنظیمات
# =========================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OMDB_TOKEN = os.environ.get("OMDB_TOKEN")

CHANNEL_ID = "@shegeftiha_iran_jahan"
CHANNEL_URL = "https://t.me/shegeftiha_iran_jahan"

favorites = {}


# =========================
# دکمه‌های عضویت
# =========================

def membership_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 عضویت در کانال",
                url=CHANNEL_URL
            )
        ],
        [
            InlineKeyboardButton(
                "✅ عضو شدم",
                callback_data="check_join"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# منوی اصلی
# =========================

def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 جستجوی آهنگ",
                callback_data="help_music"
            ),
            InlineKeyboardButton(
                "🎬 جستجوی فیلم",
                callback_data="help_movie"
            )
        ],
        [
            InlineKeyboardButton(
                "📺 جستجوی سریال",
                callback_data="help_series"
            ),
            InlineKeyboardButton(
                "📖 راهنما",
                callback_data="help_help"
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ علاقه‌مندی‌ها",
                callback_data="help_fav"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# بررسی عضویت کاربر
# =========================

async def check_membership(context, user_id):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception as e:
        print(f"Membership Error: {e}")
        return None


# =========================
# درخواست عضویت
# =========================

async def ask_for_membership(update: Update):

    text = (
        "🔐 برای استفاده از ربات ابتدا باید عضو کانال ما بشی.\n\n"
        "1️⃣ روی «📢 عضویت در کانال» بزن.\n"
        "2️⃣ داخل کانال عضو شو.\n"
        "3️⃣ برگرد و روی «✅ عضو شدم» بزن.\n\n"
        "بعد از تأیید عضویت، تمام امکانات ربات برات فعال میشه. 🎵🎬📺"
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text,
            reply_markup=membership_keyboard()
        )
    elif update.message:
        await update.message.reply_text(
            text,
            reply_markup=membership_keyboard()
        )


# =========================
# کنترل دسترسی
# =========================

async def require_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    is_member = await check_membership(
        context,
        user_id
    )

    # خطا در بررسی
    if is_member is None:

        if update.callback_query:
            await update.callback_query.answer(
                "⚠️ خطا در بررسی عضویت. لطفاً چند لحظه بعد دوباره امتحان کن.",
                show_alert=True
            )
        elif update.message:
            await update.message.reply_text(
                "⚠️ خطا در بررسی عضویت.\n\n"
                "لطفاً چند لحظه بعد دوباره امتحان کن."
            )

        return False

    # عضو نیست
    if not is_member:

        if update.callback_query:
            await update.callback_query.answer(
                "❌ هنوز عضو کانال نیستی!",
                show_alert=True
            )

            await ask_for_membership(update)

        elif update.message:
            await ask_for_membership(update)

        return False

    # عضو است
    return True


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_membership(update, context):
        return

    user_name = update.effective_user.first_name

    text = (
        f"🎵 سلام {user_name}! به MelodyHunter خوش اومدی 🎶\n\n"
        "من می‌تونم برات آهنگ، فیلم و سریال پیدا کنم! 🎧🎬📺\n\n"
        "🔍 امکانات ربات:\n\n"
        "🎵 جستجوی آهنگ\n"
        "🎬 جستجوی فیلم سینمایی\n"
        "📺 جستجوی سریال\n"
        "👤 جستجوی خواننده\n"
        "⭐ ذخیره آهنگ‌های موردعلاقه\n\n"
        "👇 از منوی زیر انتخاب کن یا اسم آهنگ موردنظرت رو بفرست."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu_keyboard()
    )


# =========================
# /help
# =========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_membership(update, context):
        return

    await update.message.reply_text(
        "📖 راهنمای ربات MelodyHunter\n\n"
        "🎵 جستجوی آهنگ:\n"
        "فقط اسم آهنگ یا خواننده رو بنویس.\n"
        "مثال: Ed Sheeran\n\n"
        "👤 جستجوی خواننده:\n"
        "/artist Ed Sheeran\n\n"
        "🎬 جستجوی فیلم:\n"
        "/movie Inception\n\n"
        "📺 جستجوی سریال:\n"
        "/series Breaking Bad\n\n"
        "⭐ آهنگ‌های موردعلاقه:\n"
        "/favorites"
    )


# =========================
# علاقه‌مندی‌ها
# =========================

async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_membership(update, context):
        return

    user_id = update.effective_user.id

    if user_id not in favorites or not favorites[user_id]:

        await update.message.reply_text(
            "❌ هنوز هیچ آهنگی ذخیره نکردی."
        )

        return

    await update.message.reply_text(
        "⭐ آهنگ‌های موردعلاقه‌ت:"
    )

    for fav in favorites[user_id]:

        message = (
            f"🎵 {fav['title']}\n"
            f"👤 خواننده: {fav['artist']}"
        )

        buttons = []

        if fav.get("preview") and fav.get("link"):

            buttons.append([
                InlineKeyboardButton(
                    "🔊 پیش‌نمایش",
                    url=fav["preview"]
                ),
                InlineKeyboardButton(
                    "🔗 لینک کامل",
                    url=fav["link"]
                )
            ])

        reply_markup = (
            InlineKeyboardMarkup(buttons)
            if buttons
            else None
        )

        await update.message.reply_text(
            message,
            reply_markup=reply_markup
        )


# =========================
# ارسال آهنگ
# =========================

async def send_song_with_buttons(update, track, artist_name):

    title = track["title"]

    preview = track.get("preview", "")
    link = track.get("link", "")

    message = (
        f"🎵 {title}\n"
        f"👤 خواننده: {artist_name}\n"
    )

    buttons = []

    if preview and link:

        buttons.append([
            InlineKeyboardButton(
                "🔊 پیش‌نمایش",
                url=preview
            ),
            InlineKeyboardButton(
                "🔗 لینک کامل",
                url=link
            )
        ])

    elif preview:

        buttons.append([
            InlineKeyboardButton(
                "🔊 پیش‌نمایش",
                url=preview
            )
        ])

    elif link:

        buttons.append([
            InlineKeyboardButton(
                "🔗 لینک کامل",
                url=link
            )
        ])

    if link:

        buttons.append([
            InlineKeyboardButton(
                "⭐ ذخیره",
                callback_data=f"fav|{title}|{artist_name}"
            ),
            InlineKeyboardButton(
                "📤 اشتراک‌گذاری",
                callback_data=f"share|{link}"
            )
        ])

    reply_markup = (
        InlineKeyboardMarkup(buttons)
        if buttons
        else None
    )

    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )


# =========================
# جستجوی خواننده
# =========================

async def artist_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_membership(update, context):
        return

    if not context.args:

        await update.message.reply_text(
            "❌ لطفاً اسم خواننده رو هم بنویس.\n"
            "مثال:\n"
            "/artist Ed Sheeran"
        )

        return

    artist_name = " ".join(context.args)

    await update.message.reply_text(
        f"🔍 در حال جستجوی آهنگ‌های {artist_name} ..."
    )

    try:

        url = (
            f"https://api.deezer.com/search/artist"
            f"?q={artist_name}&limit=1"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        if not data.get("data"):

            await update.message.reply_text(
                "❌ خواننده‌ای با این اسم پیدا نشد."
            )

            return

        artist_id = data["data"][0]["id"]
        artist_real_name = data["data"][0]["name"]

        tracks_url = (
            f"https://api.deezer.com/artist/"
            f"{artist_id}/top?limit=1"
        )

        tracks_response = requests.get(
            tracks_url,
            timeout=15
        )

        tracks_data = tracks_response.json()

        if not tracks_data.get("data"):

            await update.message.reply_text(
                "❌ آهنگی از این خواننده پیدا نشد."
            )

            return

        await update.message.reply_text(
            f"🎵 آهنگ برتر {artist_real_name}:"
        )

        await send_song_with_buttons(
            update,
            tracks_data["data"][0],
            artist_real_name
        )

    except Exception as e:

        print(f"Artist Error: {e}")

        await update.message.reply_text(
            "⚠️ خطا در جستجو. لطفاً بعداً امتحان کن."
        )


# =========================
# جستجوی فیلم
# =========================

async def movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_membership(update, context):
        return

    if not context.args:

        await update.message.reply_text(
            "❌ لطفاً اسم فیلم رو هم بنویس.\n"
            "مثال:\n"
            "/movie Inception"
        )

        return

    movie_name = " ".join(context.args)

    await update.message.reply_text(
        f"🎬 در حال جستجوی فیلم {movie_name} ..."
    )

    try:

        url = "https://www.omdbapi.com/"

        params = {
            "apikey": OMDB_TOKEN,
            "t": movie_name,
            "plot": "short"
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        data = response.json()

        if data.get("Response") == "False":

            await update.message.reply_text(
                f"❌ فیلمی با اسم «{movie_name}» پیدا نشد."
            )

            return

        title = data.get("Title", "ناشناس")
        year = data.get("Year", "ناشناس")
        genre = data.get("Genre", "ناشناس")
        director = data.get("Director", "ناشناس")
        actors = data.get("Actors", "ناشناس")
        plot = data.get("Plot", "ناشناس")
        poster = data.get("Poster", "")
        imdb_rating = data.get("imdbRating", "ناشناس")
        imdb_id = data.get("imdbID", "")

        imdb_link = f"https://www.imdb.com/title/{imdb_id}"

        message = (
            f"🎬 {title} ({year})\n\n"
            f"🎭 ژانر: {genre}\n"
            f"🎥 کارگردان: {director}\n"
            f"👥 بازیگران: {actors}\n"
            f"⭐ امتیاز IMDb: {imdb_rating}\n\n"
            f"📝 خلاصه: {plot}\n"
        )

        buttons = [
            [
                InlineKeyboardButton(
                    "🔗 صفحه IMDb",
                    url=imdb_link
                )
            ]
        ]

        if poster and poster != "N/A":

            buttons.append([
                InlineKeyboardButton(
                    "🖼️ پوستر فیلم",
                    url=poster
                )
            ])

        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:

        print(f"Movie Error: {e}")

        await update.message.reply_text(
            "⚠️ خطا در جستجوی فیلم. لطفاً بعداً امتحان کن."
        )


# =========================
# جستجوی سریال
# =========================

async def series_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_membership(update, context):
        return

    if not context.args:

        await update.message.reply_text(
            "❌ لطفاً اسم سریال رو هم بنویس.\n"
            "مثال:\n"
            "/series Breaking Bad"
        )

        return

    series_name = " ".join(context.args)

    await update.message.reply_text(
        f"📺 در حال جستجوی سریال {series_name} ..."
    )

    try:

        url = "https://www.omdbapi.com/"

        params = {
            "apikey": OMDB_TOKEN,
            "t": series_name,
            "plot": "short",
            "type": "series"
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        data = response.json()

        if data.get("Response") == "False":

            await update.message.reply_text(
                f"❌ سریالی با اسم «{series_name}» پیدا نشد."
            )

            return

        title = data.get("Title", "ناشناس")
        year = data.get("Year", "ناشناس")
        genre = data.get("Genre", "ناشناس")
        director = data.get("Director", "ناشناس")
        actors = data.get("Actors", "ناشناس")
        plot = data.get("Plot", "ناشناس")
        poster = data.get("Poster", "")
        imdb_rating = data.get("imdbRating", "ناشناس")
        total_seasons = data.get("totalSeasons", "ناشناس")
        imdb_id = data.get("imdbID", "")

        imdb_link = f"https://www.imdb.com/title/{imdb_id}"

        message = (
            f"📺 {title} ({year})\n\n"
            f"🎭 ژانر: {genre}\n"
            f"🎥 کارگردان: {director}\n"
            f"👥 بازیگران: {actors}\n"
            f"📺 تعداد فصل‌ها: {total_seasons}\n"
            f"⭐ امتیاز IMDb: {imdb_rating}\n\n"
            f"📝 خلاصه: {plot}\n"
        )

        buttons = [
            [
                InlineKeyboardButton(
                    "🔗 صفحه IMDb",
                    url=imdb_link
                )
            ]
        ]

        if poster and poster != "N/A":

            buttons.append([
                InlineKeyboardButton(
                    "🖼️ پوستر سریال",
                    url=poster
                )
            ])

        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:

        print(f"Series Error: {e}")

        await update.message.reply_text(
            "⚠️ خطا در جستجوی سریال. لطفاً بعداً امتحان کن."
        )


# =========================
# جستجوی آهنگ
# =========================

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_membership(update, context):
        return

    query = update.message.text

    await update.message.reply_text(
        f"🔍 در حال جستجو برای: {query} ..."
    )

    try:

        url = (
            f"https://api.deezer.com/search"
            f"?q={query}&limit=1"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        if not data.get("data"):

            await update.message.reply_text(
                "❌ متأسفانه آهنگی پیدا نشد. یه اسم دیگه امتحان کن."
            )

            return

        track = data["data"][0]

        await send_song_with_buttons(
            update,
            track,
            track["artist"]["name"]
        )

    except Exception as e:

        print(f"Music Error: {e}")

        await update.message.reply_text(
            "⚠️ خطا در جستجو. لطفاً بعداً امتحان کن."
        )


# =========================
# مدیریت دکمه‌ها
# =========================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =================================
    # بررسی عضویت
    # =================================

    if data == "check_join":

        user_id = update.effective_user.id

        is_member = await check_membership(
            context,
            user_id
        )

        if is_member is None:

            await query.answer(
                "⚠️ خطا در بررسی عضویت. چند لحظه بعد دوباره امتحان کن.",
                show_alert=True
            )

            return

        if not is_member:

            await query.answer(
                "❌ هنوز عضو کانال نشدی!\n"
                "اول عضو شو و دوباره امتحان کن.",
                show_alert=True
            )

            return

        # ==============================
        # عضویت تأیید شد
        # ==============================

        user_name = update.effective_user.first_name

        text = (
            f"🎉 عالیه {user_name}!\n\n"
            "✅ عضویتت با موفقیت تأیید شد.\n\n"
            "حالا تمام امکانات ربات برایت فعال است. 🎵🎬📺\n\n"
            "👇 از منوی زیر انتخاب کن یا اسم آهنگ موردنظرت رو بفرست."
        )

        await query.edit_message_text(
            text,
            reply_markup=main_menu_keyboard()
        )

        return

    # =================================
    # از اینجا به بعد همه دکمه‌ها
    # دوباره عضویت را بررسی می‌کنند
    # =================================

    is_member = await check_membership(
        context,
        update.effective_user.id
    )

    if is_member is None:

        await query.answer(
            "⚠️ خطا در بررسی عضویت.",
            show_alert=True
        )

        return

    if not is_member:

        await query.answer(
            "❌ برای استفاده از این بخش باید عضو کانال باشی.",
            show_alert=True
        )

        await ask_for_membership(update)

        return

    # =================================
    # جستجوی آهنگ
    # =================================

    if data == "help_music":

        await query.message.reply_text(
            "🎵 برای جستجوی آهنگ:\n\n"
            "فقط اسم آهنگ یا خواننده رو بفرست.\n\n"
            "مثال:\n"
            "Shape of You\n\n"
            "یا:\n"
            "Ed Sheeran"
        )

    # =================================
    # راهنما
    # =================================

    elif data == "help_help":

        await query.message.reply_text(
            "📖 راهنمای کامل MelodyHunter\n\n"
            "🎵 آهنگ:\n"
            "اسم آهنگ یا خواننده رو بفرست.\n\n"
            "👤 خواننده:\n"
            "/artist Ed Sheeran\n\n"
            "🎬 فیلم:\n"
            "/movie Inception\n\n"
            "📺 سریال:\n"
            "/series Breaking Bad\n\n"
            "⭐ علاقه‌مندی‌ها:\n"
            "/favorites"
        )

    # =================================
    # علاقه‌مندی‌ها
    # =================================

    elif data == "help_fav":

        user_id = update.effective_user.id

        if user_id not in favorites or not favorites[user_id]:

            await query.message.reply_text(
                "❌ هنوز هیچ آهنگی ذخیره نکردی."
            )

            return

        await query.message.reply_text(
            "⭐ آهنگ‌های موردعلاقه‌ت:"
        )

        for fav in favorites[user_id]:

            await query.message.reply_text(
                f"🎵 {fav['title']}\n"
                f"👤 خواننده: {fav['artist']}"
            )

    # =================================
    # فیلم
    # =================================

    elif data == "help_movie":

        await query.message.reply_text(
            "🎬 برای جستجوی فیلم:\n\n"
            "دستور زیر را بنویس:\n\n"
            "/movie Inception"
        )

    # =================================
    # سریال
    # =================================

    elif data == "help_series":

        await query.message.reply_text(
            "📺 برای جستجوی سریال:\n\n"
            "دستور زیر را بنویس:\n\n"
            "/series Breaking Bad"
        )

    # =================================
    # ذخیره آهنگ
    # =================================

    elif data.startswith("fav|"):

        parts = data.split("|", 2)

        if len(parts) < 3:
            return

        title = parts[1]
        artist = parts[2]

        user_id = update.effective_user.id

        if user_id not in favorites:
            favorites[user_id] = []

        favorites[user_id].append({
            "title": title,
            "artist": artist,
            "preview": "",
            "link": ""
        })

        await query.answer(
            "⭐ آهنگ ذخیره شد!",
            show_alert=True
        )

    # =================================
    # اشتراک‌گذاری
    # =================================

    elif data.startswith("share|"):

        link = data.replace(
            "share|",
            "",
            1
        )

        share_text = (
            f"🎵 این آهنگ رو از MelodyHunter پیدا کردم:\n"
            f"{link}"
        )

        await query.message.reply_text(
            f"📤 متن اشتراک‌گذاری:\n\n"
            f"{share_text}"
        )


# =========================
# اجرای ربات
# =========================

if __name__ == "__main__":

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN در Environment Variables تنظیم نشده است."
        )

    if not OMDB_TOKEN:
        print(
            "⚠️ هشدار: OMDB_TOKEN تنظیم نشده است."
        )

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("artist", artist_search)
    )

    application.add_handler(
        CommandHandler("movie", movie_search)
    )

    application.add_handler(
        CommandHandler("series", series_search)
    )

    application.add_handler(
        CommandHandler("favorites", favorites_command)
    )

    application.add_handler(
        CallbackQueryHandler(button_callback)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_music
        )
    )

    print("Bot is running...")

    application.run_polling()
