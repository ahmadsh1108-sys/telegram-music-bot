import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@shegeftiha_iran_jahan"
CHANNEL_URL = "https://t.me/shegeftiha_iran_jahan"

# ذخیره آهنگ‌های موردعلاقه (در حافظه)
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
        "📖 **راهنمای ربات MelodyHunter**\n\n"
        "🔍 **جستجوی آهنگ:**\n"
        "فقط اسم آهنگ یا خواننده رو بنویس (مثلاً: Ed Sheeran)\n\n"
        "👤 **جستجوی خواننده:**\n"
        "دستور /artist و بعد اسم خواننده\n"
        "مثال: /artist Ed Sheeran\n\n"
        "⭐ **ذخیره آهنگ:**\n"
        "روی دکمه ⭐ ذخیره بزن تا آهنگ به لیست علاقه‌مندی‌هات اضافه بشه\n\n"
        "📤 **اشتراک‌گذاری:**\n"
        "روی دکمه 📤 بزن تا لینک آهنگ رو برای دوستت بفرستی\n\n"
        "🎵 **پیشنهاد مشابه:**\n"
        "روی دکمه 🎵 مشابه بزن تا آهنگ‌های مشابه ببینی\n\n"
        "❤️ **آهنگ‌های موردعلاقه:**\n"
        "دستور /favorites برای دیدن لیست ذخیره شده‌ها",
        parse_mode='Markdown'
    )

async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return
    user_id = update.effective_user.id
    if user_id not in favorites or not favorites[user_id]:
        await update.message.reply_text("❌ هنوز هیچ آهنگی ذخیره نکردی.")
        return
    
    await update.message.reply_text("⭐ **آهنگ‌های موردعلاقه‌ت:**", parse_mode='Markdown')
    for fav in favorites[user_id]:
        message = f"🎵 **{fav['title']}**\n👤 خواننده: {fav['artist']}"
        buttons = []
        if fav.get('preview'):
            buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=fav['preview'])])
        if fav.get('link'):
            buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=fav['link'])])
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

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
        
        await update.message.reply_text(f"🎵 **آهنگ‌های برتر {artist_real_name}:**", parse_mode='Markdown')
        
        for track in tracks_data['data']:
            await send_song_with_buttons(update, track, artist_real_name)
    
    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

async def send_song_with_buttons(update, track, artist_name):
    title = track['title']
    preview = track.get('preview', '')
    link = track.get('link', '')
    
    message = f"🎵 **{title}**\n👤 خواننده: {artist_name}\n"
    
    # دکمه‌های شیشه‌ای
    buttons = []
    if preview:
        buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=preview)])
    if link:
        buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=link)])
        buttons.append([InlineKeyboardButton("⭐ ذخیره", callback_data=f"fav_{title}_{artist_name}")])
        buttons.append([InlineKeyboardButton("📤 اشتراک‌گذاری", callback_data=f"share_{link}")])
        buttons.append([InlineKeyboardButton("🎵 مشابه", callback_data=f"similar_{title}_{artist_name}")])
    
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

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
            # جستجو در رادیو جوان برای آهنگ‌های ایرانی
            await search_radio_javan(update, query)
            return
        
        for track in data['data']:
            await send_song_with_buttons(update, track, track['artist']['name'])
    
    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

async def search_radio_javan(update, query):
    """جستجو در رادیو جوان برای آهنگ‌های ایرانی"""
    try:
        # استفاده از API رادیو جوان برای جستجو
        url = f"https://api.radiojavan.com/v1/search?q={query}&limit=5"
        response = requests.get(url)
        data = response.json()
        
        if not data.get('results'):
            await update.message.reply_text("❌ متأسفانه آهنگی پیدا نشد. یه اسم دیگه امتحان کن.")
            return
        
        await update.message.reply_text(f"🎵 **نتایج جستجو برای {query}:**", parse_mode='Markdown')
        
        for track in data['results']:
            title = track.get('title', 'ناشناس')
            artist = track.get('artist', 'ناشناس')
            download_url = track.get('download_url', '')
            
            message = f"🎵 **{title}**\n👤 خواننده: {artist}\n"
            
            buttons = []
            if download_url:
                buttons.append([InlineKeyboardButton("🔊 دانلود", url=download_url)])
            
            reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    except Exception as e:
        await update.message.reply_text("❌ متأسفانه آهنگی پیدا نشد. یه اسم دیگه امتحان کن.")
        print(f"Radio Javan Error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # ذخیره آهنگ
    if data.startswith("fav_"):
        parts = data.split("_", 2)
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
        
        await query.edit_message_text(f"⭐ آهنگ **{title}** از **{artist}** ذخیره شد!", parse_mode='Markdown')
    
    # اشتراک‌گذاری
    elif data.startswith("share_"):
        link = data.replace("share_", "")
        share_text = f"🎵 این آهنگ رو از MelodyHunter پیدا کردم:\n{link}"
        await query.edit_message_text(f"📤 **متن اشتراک‌گذاری:**\n\n{share_text}", parse_mode='Markdown')
    
    # آهنگ مشابه
    elif data.startswith("similar_"):
        parts = data.split("_", 2)
        title = parts[1]
        artist = parts[2]
        await query.edit_message_text(f"🔍 در حال جستجوی آهنگ‌های مشابه با **{title}** از **{artist}** ...", parse_mode='Markdown')
        
        # جستجو در Deezer برای آهنگ‌های مشابه
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
                    
                    message = f"🎵 **{similar_title}**\n👤 خواننده: {similar_artist}\n"
                    buttons = []
                    if preview:
                        buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=preview)])
                    if link:
                        buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=link)])
                    
                    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
                    await query.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            print(f"Similar Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("artist", artist_search))
    application.add_handler(CommandHandler("favorites", favorites_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("Bot is running...")
    application.run_polling()
