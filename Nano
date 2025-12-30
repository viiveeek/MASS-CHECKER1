# ================== CONFIG ==================
BOT_TOKEN = "8286097606:AAGhG5eGSKQvYcAghCnMK0gGz_vPZi2pQNY"
ADMIN_ID = 8153642807 # YOUR TELEGRAM ID

DEFAULT_LIMIT = 100
DEFAULT_COOLDOWN = 600  # seconds
DEFAULT_API_URL = "http://127.0.0.1:5000/check" 
DEFAULT_PHOTO = "https://i.imgur.com/xxxx.jpg"
CHANNEL_ID = -1001234567890 

import time
import json
import asyncio
import aiohttp
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ================== MEMORY ==================
premium_users = set()
user_cooldown = {}
user_settings = {}
bot_settings = {
    "limit": DEFAULT_LIMIT,
    "cooldown": DEFAULT_COOLDOWN,
    "api": DEFAULT_API_URL,
    "photo": DEFAULT_PHOTO,
    "channel": CHANNEL_ID
}

# ================== UTIL ==================
def is_admin(uid): return uid == ADMIN_ID
def now(): return int(time.time())

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in premium_users and not is_admin(uid):
        await update.message.reply_text(
            "❌ Access Denied\n\nThis is a Premium Bot\nBuy Premium ➜ @WANG_WEBS"
        )
        return
    await update.message.reply_text("✅ Send .txt file")

# ================== FILE HANDLER ==================
async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in premium_users and not is_admin(uid):
        return

    if uid in user_cooldown and now() < user_cooldown[uid]:
        await update.message.reply_text("⏳ Cooling Time Active\nPlease wait")
        return

    doc = update.message.document
    file = await doc.get_file()
    content = (await file.download_as_bytearray()).decode()
    lines = [x.strip() for x in content.splitlines() if x.strip()]
    limit = bot_settings["limit"]

    context.user_data["ccs"] = lines[:limit]
    context.user_data["stop"] = False

    text = (
        "⏳ Your File Detected\n\n"
        f"📊 CC Found ➜ {len(lines)}\n"
        f"💎 Your Limit ➜ {limit}\n\n"
        "Click On Check CC To Start 😎"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Check CC", callback_data="start_check")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

    await update.message.reply_text(text, reply_markup=kb)


#Implemented Intergration ApiXmassChecker
async def start_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    approved = 0
    declined = 0
    ccs = context.user_data.get("ccs", [])
    total = len(ccs)
    status_msg = await q.message.edit_text(
        f"Cooking 🔥 CC One by One...\n\n⏳ Progress ➜ 0 / {total}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 STOP", callback_data="stop")]]),
        parse_mode="HTML" 
    )

    async with aiohttp.ClientSession() as session:
        for i, cc in enumerate(ccs, start=1):
            if context.user_data.get("stop"): break

            try:
                async with session.post(bot_settings["api"], json={"cc": cc}, timeout=20) as r:
                    data = await r.json()
                    status = data.get("status", "declined")
                    bank = data.get("bank", "Unknown")
                    country = data.get("country", "Unknown")
            except:
                status, bank, country = "declined", "N/A", "N/A"

            if status == "approved":
                approved += 1
                msg = (
                    "<b>✅ APPROVED</b>\n\n"
                    f"💳 <b>CC ➜</b> <code>{cc}</code>\n"
                    f"🏦 <b>Bank ➜</b> {bank}\n"
                    f"🌍 <b>Country ➜</b> {country}\n\n"
                    f"<b>Checked By ➜</b> @WANG_WEBS"
                )
                await context.bot.send_message(uid, msg, parse_mode="HTML")
            else:
                declined += 1
            await status_msg.edit_text(
                f"Cooking 🔥 CC One by One...\n\n"
                f"Current ➜ <code>{cc}</code>\n"
                f"✅ Approved ➜ {approved}\n"
                f"❌ Declined ➜ {declined}\n\n"
                f"⏳ Progress ➜ {i} / {total}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 STOP", callback_data="stop")]]),
                parse_mode="HTML"
            )
            await asyncio.sleep(1)

    user_cooldown[uid] = now() + bot_settings["cooldown"]

# ================== STOP / CANCEL ==================
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stop"] = True
    await update.callback_query.answer("Stopped")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("❌ Cancelled")

# ================== ADMIN PANEL ==================
async def addpremium(update: Update, context):
    if not is_admin(update.effective_user.id): return
    premium_users.add(int(context.args[0]))
    await update.message.reply_text("✅ Added")

async def setapi(update: Update, context):
    if not is_admin(update.effective_user.id): return
    bot_settings["api"] = context.args[0]
    await update.message.reply_text("✅ API Updated")

async def backup(update: Update, context):
    if not is_admin(update.effective_user.id): return
    data = {
        "premium": list(premium_users),
        "settings": bot_settings
    }
    with open("backup.json", "w") as f:
        json.dump(data, f)
    await update.message.reply_text("✅ Backup Saved")

async def restore(update: Update, context):
    if not is_admin(update.effective_user.id): return
    with open("backup.json") as f:
        data = json.load(f)
    premium_users.update(data["premium"])
    bot_settings.update(data["settings"])
    await update.message.reply_text("✅ Restored")

# ================== MAIN ==================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addpremium", addpremium))
app.add_handler(CommandHandler("setapi", setapi))
app.add_handler(CommandHandler("backup", backup))
app.add_handler(CommandHandler("restore", restore))
app.add_handler(MessageHandler(filters.Document.TEXT, file_handler))
app.add_handler(CallbackQueryHandler(start_check, pattern="start_check"))
app.add_handler(CallbackQueryHandler(stop, pattern="stop"))
app.add_handler(CallbackQueryHandler(cancel, pattern="cancel"))

app.run_polling()
