import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@shegeftiha_iran_jahan"
CHANNEL_URL = "https://t.me/shegeftiha_iran_jahan"

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
        "فقط اسم آهنگ رو بنویس (مثلاً: Shape of You)\n\n"
        "👤 **جستجوی خواننده:**\n"
        "دستور /artist و بعد اسم خواننده\n"
        "مثال: /artist Ed Sheeran\n\n"
        "💡 **نکته:**\n"
        "برای هر آهنگ، دکمه‌های پیش‌نمایش و لینک کامل وجود داره.",
        parse_mode='Markdown'
    )

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
            title = track['title']
            preview = track.get('preview', '')
            link = track.get('link', '')
            
            message = f"🎵 **{title}**\n👤 خواننده: {artist_real_name}\n"
            
            buttons = []
            if preview:
                buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=preview)])
            if link:
                buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=link)])
            
            reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

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
            title = track['title']
            artist = track['artist']['name']
            preview = track.get('preview', '')
            link = track.get('link', '')
            
            message = f"🎵 **{title}**\n👤 خواننده: {artist}\n"
            
            buttons = []
            if preview:
                buttons.append([InlineKeyboardButton("🔊 پیش‌نمایش", url=preview)])
            if link:
                buttons.append([InlineKeyboardButton("🔗 لینک کامل", url=link)])
            
            reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("artist", artist_search))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("Bot is running...")
    application.run_polling()
