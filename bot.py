import os
import requests
from urllib.parse import quote

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

# برای پشتیبان فیلم و سریال
OMDB_TOKEN = os.environ.get("OMDB_TOKEN")

# توکن TMDB
TMDB_TOKEN = os.environ.get("TMDB_TOKEN")

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
# بررسی عضویت
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
# کنترل عضویت
# =========================

async def require_membership(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    is_member = await check_membership(
        context,
        user_id
    )

    if is_member is None:

        if update.callback_query:

            await update.callback_query.answer(
                "⚠️ خطا در بررسی عضویت. چند لحظه بعد دوباره امتحان کن.",
                show_alert=True
            )

        elif update.message:

            await update.message.reply_text(
                "⚠️ خطا در بررسی عضویت.\n\n"
                "لطفاً چند لحظه بعد دوباره امتحان کن."
            )

        return False

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

    return True


# =========================
# /start
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not await require_membership(update, context):
        return

    await update.message.reply_text(
        "📖 راهنمای ربات MelodyHunter\n\n"

        "🎵 جستجوی آهنگ:\n"
        "اسم آهنگ یا خواننده رو بنویس.\n"
        "مثال:\n"
        "محسن چاوشی\n"
        "یا:\n"
        "Shape of You\n\n"

        "👤 جستجوی خواننده:\n"
        "/artist Ed Sheeran\n\n"

        "🎬 جستجوی فیلم:\n"
        "/movie Inception\n"
        "یا:\n"
        "/movie متری شیش و نیم\n\n"

        "📺 جستجوی سریال:\n"
        "/series Breaking Bad\n"
        "یا:\n"
        "/series پایتخت\n\n"

        "⭐ علاقه‌مندی‌ها:\n"
        "/favorites"
    )


# =========================
# علاقه‌مندی‌ها
# =========================

async def favorites_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

        elif fav.get("link"):

            buttons.append([
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

async def send_song_with_buttons(
    update,
    track,
    artist_name
):

    title = track.get("title", "نامشخص")

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


# ============================================================
# جستجوی آهنگ در Deezer
# ============================================================

def search_deezer(query):

    try:

        response = requests.get(
            "https://api.deezer.com/search",
            params={
                "q": query,
                "limit": 5
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if data.get("data"):
            return data["data"][0]

    except Exception as e:

        print(f"Deezer Error: {e}")

    return None


# ============================================================
# جستجوی آهنگ
# ============================================================

async def search_music(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not await require_membership(update, context):
        return

    query = update.message.text.strip()

    if not query:
        return

    await update.message.reply_text(
        f"🔍 در حال جستجو برای:\n"
        f"🎵 {query}\n\n"
        f"لطفاً کمی صبر کن..."
    )

    try:

        # جستجوی مستقیم
        track = search_deezer(query)

        # اگر نتیجه پیدا نشد، چند مدل جستجو
        if not track:

            alternative_queries = [
                query.replace(" آهنگ", ""),
                query.replace(" song", ""),
                query.replace(" موزیک", ""),
            ]

            for alternative in alternative_queries:

                alternative = alternative.strip()

                if alternative:

                    track = search_deezer(
                        alternative
                    )

                    if track:
                        break

        if not track:

            await update.message.reply_text(
                "❌ متأسفانه آهنگی پیدا نشد.\n\n"
                "💡 اسم آهنگ یا خواننده رو کمی متفاوت امتحان کن."
            )

            return

        artist_name = (
            track.get("artist", {})
            .get("name", "نامشخص")
        )

        await send_song_with_buttons(
            update,
            track,
            artist_name
        )

    except Exception as e:

        print(f"Music Error: {e}")

        await update.message.reply_text(
            "⚠️ خطا در جستجوی آهنگ.\n"
            "لطفاً دوباره امتحان کن."
        )


# ============================================================
# جستجوی خواننده
# ============================================================

async def artist_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not await require_membership(update, context):
        return

    if not context.args:

        await update.message.reply_text(
            "❌ لطفاً اسم خواننده رو هم بنویس.\n\n"
            "مثال:\n"
            "/artist Ed Sheeran\n\n"
            "یا:\n"
            "/artist محسن چاوشی"
        )

        return

    artist_name = " ".join(context.args)

    await update.message.reply_text(
        f"🔍 در حال جستجوی آهنگ‌های {artist_name} ..."
    )

    try:

        response = requests.get(
            "https://api.deezer.com/search/artist",
            params={
                "q": artist_name,
                "limit": 1
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("data"):

            await update.message.reply_text(
                "❌ خواننده‌ای با این اسم پیدا نشد."
            )

            return

        artist_id = data["data"][0]["id"]
        artist_real_name = data["data"][0]["name"]

        tracks_response = requests.get(
            f"https://api.deezer.com/artist/"
            f"{artist_id}/top",
            params={
                "limit": 5
            },
            timeout=15
        )

        tracks_response.raise_for_status()

        tracks_data = tracks_response.json()

        if not tracks_data.get("data"):

            await update.message.reply_text(
                "❌ آهنگی از این خواننده پیدا نشد."
            )

            return

        await update.message.reply_text(
            f"🎵 چند آهنگ از {artist_real_name}:"
        )

        # حداکثر 5 آهنگ
        for track in tracks_data["data"][:5]:

            await send_song_with_buttons(
                update,
                track,
                artist_real_name
            )

    except Exception as e:

        print(f"Artist Error: {e}")

        await update.message.reply_text(
            "⚠️ خطا در جستجوی خواننده."
        )


# ============================================================
# TMDB Request
# ============================================================

def tmdb_request(endpoint, params=None):

    if not TMDB_TOKEN:
        return None

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

    try:

        response = requests.get(
            f"https://api.themoviedb.org/3/{endpoint}",
            headers=headers,
            params=params or {},
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print(f"TMDB Error: {e}")

        return None


# ============================================================
# جستجوی فیلم در TMDB
# ============================================================

def tmdb_movie_search(query):

    # ابتدا فارسی
    data = tmdb_request(
        "search/movie",
        {
            "query": query,
            "language": "fa-IR",
            "include_adult": "false",
            "page": 1
        }
    )

    if data and data.get("results"):

        return data["results"][0]

    # سپس انگلیسی
    data = tmdb_request(
        "search/movie",
        {
            "query": query,
            "language": "en-US",
            "include_adult": "false",
            "page": 1
        }
    )

    if data and data.get("results"):

        return data["results"][0]

    return None


# ============================================================
# جستجوی سریال در TMDB
# ============================================================

def tmdb_series_search(query):

    # ابتدا فارسی
    data = tmdb_request(
        "search/tv",
        {
            "query": query,
            "language": "fa-IR",
            "page": 1
        }
    )

    if data and data.get("results"):

        return data["results"][0]

    # سپس انگلیسی
    data = tmdb_request(
        "search/tv",
        {
            "query": query,
            "language": "en-US",
            "page": 1
        }
    )

    if data and data.get("results"):

        return data["results"][0]

    return None


# ============================================================
# فیلم با TMDB
# ============================================================

async def movie_search_tmdb(
    update: Update,
    movie_name
):

    result = tmdb_movie_search(movie_name)

    if not result:
        return False

    movie_id = result.get("id")

    details = tmdb_request(
        f"movie/{movie_id}",
        {
            "language": "fa-IR",
            "append_to_response": "credits"
        }
    )

    if not details:
        details = result

    title = (
        details.get("title")
        or details.get("original_title")
        or movie_name
    )

    original_title = details.get(
        "original_title",
        ""
    )

    year = "نامشخص"

    release_date = details.get(
        "release_date",
        ""
    )

    if release_date:
        year = release_date[:4]

    genres = details.get("genres", [])

    genre = ", ".join(
        g.get("name", "")
        for g in genres
        if g.get("name")
    )

    if not genre:
        genre = "نامشخص"

    credits = details.get(
        "credits",
        {}
    )

    crew = credits.get(
        "crew",
        []
    )

    directors = [
        person.get("name")
        for person in crew
        if person.get("job") == "Director"
    ]

    director = (
        ", ".join(directors)
        if directors
        else "نامشخص"
    )

    cast = credits.get(
        "cast",
        []
    )

    actors = ", ".join(
        person.get("name", "")
        for person in cast[:5]
        if person.get("name")
    )

    if not actors:
        actors = "نامشخص"

    overview = details.get(
        "overview",
        ""
    )

    if not overview:
        overview = "خلاصه‌ای ثبت نشده است."

    rating = details.get(
        "vote_average",
        0
    )

    try:
        rating = f"{float(rating):.1f}/10"
    except:
        rating = "نامشخص"

    poster_path = details.get(
        "poster_path"
    )

    poster = ""

    if poster_path:

        poster = (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    tmdb_link = (
        f"https://www.themoviedb.org/movie/{movie_id}"
    )

    message = (
        f"🎬 {title} ({year})\n\n"
    )

    if original_title and original_title != title:

        message += (
            f"🔤 عنوان اصلی: {original_title}\n\n"
        )

    message += (
        f"🎭 ژانر: {genre}\n"
        f"🎥 کارگردان: {director}\n"
        f"👥 بازیگران: {actors}\n"
        f"⭐ امتیاز TMDB: {rating}\n\n"
        f"📝 خلاصه:\n{overview}\n\n"
        f"🔎 اطلاعات: TMDB"
    )

    buttons = [
        [
            InlineKeyboardButton(
                "🔗 صفحه فیلم در TMDB",
                url=tmdb_link
            )
        ]
    ]

    if poster:

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

    return True


# ============================================================
# فیلم با OMDb - پشتیبان
# ============================================================

async def movie_search_omdb(
    update: Update,
    movie_name
):

    if not OMDB_TOKEN:
        return False

    try:

        response = requests.get(
            "https://www.omdbapi.com/",
            params={
                "apikey": OMDB_TOKEN,
                "t": movie_name,
                "plot": "short"
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "False":
            return False

        title = data.get(
            "Title",
            "ناشناس"
        )

        year = data.get(
            "Year",
            "ناشناس"
        )

        genre = data.get(
            "Genre",
            "ناشناس"
        )

        director = data.get(
            "Director",
            "ناشناس"
        )

        actors = data.get(
            "Actors",
            "ناشناس"
        )

        plot = data.get(
            "Plot",
            "ناشناس"
        )

        poster = data.get(
            "Poster",
            ""
        )

        imdb_rating = data.get(
            "imdbRating",
            "ناشناس"
        )

        imdb_id = data.get(
            "imdbID",
            ""
        )

        imdb_link = (
            f"https://www.imdb.com/title/{imdb_id}"
        )

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

        return True

    except Exception as e:

        print(f"OMDb Movie Error: {e}")

        return False


# ============================================================
# جستجوی فیلم
# ============================================================

async def movie_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not await require_membership(update, context):
        return

    if not context.args:

        await update.message.reply_text(
            "❌ لطفاً اسم فیلم رو هم بنویس.\n\n"
            "مثال:\n"
            "/movie Inception\n\n"
            "یا:\n"
            "/movie متری شیش و نیم"
        )

        return

    movie_name = " ".join(context.args)

    await update.message.reply_text(
        f"🎬 در حال جستجوی:\n"
        f"«{movie_name}» ..."
    )

    # اول TMDB
    if TMDB_TOKEN:

        found = await movie_search_tmdb(
            update,
            movie_name
        )

        if found:
            return

    # سپس OMDb
    found = await movie_search_omdb(
        update,
        movie_name
    )

    if found:
        return

    await update.message.reply_text(
        f"❌ فیلمی با اسم «{movie_name}» پیدا نشد.\n\n"
        "💡 اسم فیلم رو با شکل دیگری امتحان کن."
    )


# ============================================================
# سریال با TMDB
# ============================================================

async def series_search_tmdb(
    update: Update,
    series_name
):

    result = tmdb_series_search(
        series_name
    )

    if not result:
        return False

    series_id = result.get("id")

    details = tmdb_request(
        f"tv/{series_id}",
        {
            "language": "fa-IR",
            "append_to_response": "credits"
        }
    )

    if not details:
        details = result

    title = (
        details.get("name")
        or details.get("original_name")
        or series_name
    )

    original_title = details.get(
        "original_name",
        ""
    )

    first_air_date = details.get(
        "first_air_date",
        ""
    )

    year = (
        first_air_date[:4]
        if first_air_date
        else "نامشخص"
    )

    genres = details.get(
        "genres",
        []
    )

    genre = ", ".join(
        g.get("name", "")
        for g in genres
        if g.get("name")
    )

    if not genre:
        genre = "نامشخص"

    credits = details.get(
        "credits",
        {}
    )

    cast = credits.get(
        "cast",
        []
    )

    actors = ", ".join(
        person.get("name", "")
        for person in cast[:5]
        if person.get("name")
    )

    if not actors:
        actors = "نامشخص"

    creators = details.get(
        "created_by",
        []
    )

    creator_names = ", ".join(
        person.get("name", "")
        for person in creators
        if person.get("name")
    )

    if not creator_names:
        creator_names = "نامشخص"

    overview = details.get(
        "overview",
        ""
    )

    if not overview:
        overview = "خلاصه‌ای ثبت نشده است."

    rating = details.get(
        "vote_average",
        0
    )

    try:
        rating = f"{float(rating):.1f}/10"
    except:
        rating = "نامشخص"

    seasons = details.get(
        "number_of_seasons",
        "نامشخص"
    )

    episodes = details.get(
        "number_of_episodes",
        "نامشخص"
    )

    poster_path = details.get(
        "poster_path"
    )

    poster = ""

    if poster_path:

        poster = (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    tmdb_link = (
        f"https://www.themoviedb.org/tv/{series_id}"
    )

    message = (
        f"📺 {title} ({year})\n\n"
    )

    if original_title and original_title != title:

        message += (
            f"🔤 عنوان اصلی: {original_title}\n\n"
        )

    message += (
        f"🎭 ژانر: {genre}\n"
        f"🎥 سازنده: {creator_names}\n"
        f"👥 بازیگران: {actors}\n"
        f"📺 تعداد فصل‌ها: {seasons}\n"
        f"🎞️ تعداد قسمت‌ها: {episodes}\n"
        f"⭐ امتیاز TMDB: {rating}\n\n"
        f"📝 خلاصه:\n{overview}\n\n"
        f"🔎 اطلاعات: TMDB"
    )

    buttons = [
        [
            InlineKeyboardButton(
                "🔗 صفحه سریال در TMDB",
                url=tmdb_link
            )
        ]
    ]

    if poster:

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

    return True


# ============================================================
# سریال با OMDb - پشتیبان
# ============================================================

async def series_search_omdb(
    update: Update,
    series_name
):

    if not OMDB_TOKEN:
        return False

    try:

        response = requests.get(
            "https://www.omdbapi.com/",
            params={
                "apikey": OMDB_TOKEN,
                "t": series_name,
                "plot": "short",
                "type": "series"
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "False":
            return False

        title = data.get(
            "Title",
            "ناشناس"
        )

        year = data.get(
            "Year",
            "ناشناس"
        )

        genre = data.get(
            "Genre",
            "ناشناس"
        )

        director = data.get(
            "Director",
            "ناشناس"
        )

        actors = data.get(
            "Actors",
            "ناشناس"
        )

        plot = data.get(
            "Plot",
            "ناشناس"
        )

        poster = data.get(
            "Poster",
            ""
        )

        imdb_rating = data.get(
            "imdbRating",
            "ناشناس"
        )

        total_seasons = data.get(
            "totalSeasons",
            "ناشناس"
        )

        imdb_id = data.get(
            "imdbID",
            ""
        )

        imdb_link = (
            f"https://www.imdb.com/title/{imdb_id}"
        )

        message = (
            f"📺 {title} ({year})\n\n"
            f"🎭 ژانر: {genre}\n"
            f"🎥 سازنده/کارگردان: {director}\n"
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

        return True

    except Exception as e:

        print(f"OMDb Series Error: {e}")

        return False


# ============================================================
# جستجوی سریال
# ============================================================

async def series_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not await require_membership(update, context):
        return

    if not context.args:

        await update.message.reply_text(
            "❌ لطفاً اسم سریال رو هم بنویس.\n\n"
            "مثال:\n"
            "/series Breaking Bad\n\n"
            "یا:\n"
            "/series پایتخت"
        )

        return

    series_name = " ".join(context.args)

    await update.message.reply_text(
        f"📺 در حال جستجوی:\n"
        f"«{series_name}» ..."
    )

    # اول TMDB
    if TMDB_TOKEN:

        found = await series_search_tmdb(
            update,
            series_name
        )

        if found:
            return

    # سپس OMDb
    found = await series_search_omdb(
        update,
        series_name
    )

    if found:
        return

    await update.message.reply_text(
        f"❌ سریالی با اسم «{series_name}» پیدا نشد.\n\n"
        "💡 اسم سریال رو با شکل دیگری امتحان کن."
    )


# ============================================================
# مدیریت دکمه‌ها
# ============================================================

async def button_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    data = query.data

    # =================================
    # بررسی عضویت
    # =================================

    if data == "check_join":

        await query.answer()

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
    # بررسی عضویت برای سایر دکمه‌ها
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

    await query.answer()

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
            "محسن چاوشی"
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
            "/movie Inception\n"
            "/movie متری شیش و نیم\n\n"

            "📺 سریال:\n"
            "/series Breaking Bad\n"
            "/series پایتخت\n\n"

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
            "/movie Inception\n\n"
            "یا برای فیلم ایرانی:\n"
            "/movie متری شیش و نیم"
        )

    # =================================
    # سریال
    # =================================

    elif data == "help_series":

        await query.message.reply_text(
            "📺 برای جستجوی سریال:\n\n"
            "دستور زیر را بنویس:\n\n"
            "/series Breaking Bad\n\n"
            "یا برای سریال ایرانی:\n"
            "/series پایتخت"
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

        # جلوگیری از ذخیره تکراری
        exists = any(
            fav["title"] == title
            and fav["artist"] == artist
            for fav in favorites[user_id]
        )

        if exists:

            await query.answer(
                "⭐ این آهنگ قبلاً ذخیره شده.",
                show_alert=True
            )

            return

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


# ============================================================
# اجرای ربات
# ============================================================

if __name__ == "__main__":

    if not BOT_TOKEN:

        raise ValueError(
            "BOT_TOKEN در Environment Variables تنظیم نشده است."
        )

    if not OMDB_TOKEN:

        print(
            "⚠️ هشدار: OMDB_TOKEN تنظیم نشده است."
        )

    if not TMDB_TOKEN:

        print(
            "⚠️ هشدار: TMDB_TOKEN تنظیم نشده است."
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

    print("MelodyHunter is running...")

    application.run_polling()
