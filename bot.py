import os
import requests
from telegram import Update
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
    await update.message.reply_text("🎵 سلام! اسم آهنگ یا خواننده مورد نظرت رو بفرست تا برات پیدا کنم.")

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
            if preview:
                message += f"🔊 پیش‌نمایش: [کلیک کن]({preview})\n"
            if link:
                message += f"🔗 [لینک کامل]({link})"
            
            await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text("⚠️ خطا در جستجو. لطفاً بعداً امتحان کن.")
        print(f"Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("Bot is running...")
    application.run_polling()
