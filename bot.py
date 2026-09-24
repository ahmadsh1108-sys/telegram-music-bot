import os
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
    await update.message.reply_text("🎵 سلام! اسم آهنگ یا خواننده مورد نظرت رو بفرست.")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        return
    query = update.message.text
    await update.message.reply_text(f"🔍 در حال جستجو برای: {query} ...")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("Bot is running...")
    application.run_polling()
