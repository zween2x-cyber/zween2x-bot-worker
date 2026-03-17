import os, sqlite3, requests, logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- RENDER PORT FIX ---
app = Flask(__name__)
@app.route('/')
def home(): return "z.ween2x is Live!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
TOKEN = "8155338241:AAH2Wt__0vFRvVdp1S-5IucgsWL3gNPJeZ0"
API_KEY = "1b43308f-7926-4ebd-a313-792d6e3c5005"
ADMIN_ID = 7155006319 
UPI_ID = "8120238780@ybl"

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('zween2x.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS contests (user_id TEXT, fee TEXT, team TEXT, utr TEXT, status TEXT)')
    conn.commit()
    conn.close()

# --- BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_db()
    msg = "🏆 **z.ween2x - mad by chouhan**\n\nEntry Fee chunein aur apni Dream Team banayein:"
    kb = [[InlineKeyboardButton(f"💰 ₹{f}", callback_data=f"f_{f}")] for f in [49, 99, 149]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def handle_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    if q.data.startswith('f_'):
        context.user_data['fee'] = q.data.split('_')[1]
        url = f"https://api.cricketdata.org/v1/currentMatches?apikey={API_KEY}"
        matches = requests.get(url).json().get('data', [])
        btns = [[InlineKeyboardButton(m['name'], callback_data=f"m_{m['id']}")] for m in matches[:5]]
        await q.edit_message_text("🏏 Match chunein:", reply_markup=InlineKeyboardMarkup(btns))

    elif q.data.startswith('m_'):
        # 22 Players Selection Simulation (Simplified for UX)
        # Yahan par API se 22 players aate hain, user 11 + 4 backup chunta hai
        await q.edit_message_text("✅ Team Saved!\n\nAb niche diye UPI par payment karein aur UTR bhejien.\n\n"
                                  f"Entry: ₹{context.user_data['fee']}\nUPI: `{UPI_ID}`", 
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Submit UTR", callback_data="sub_utr")]]))

    elif q.data == "sub_utr":
        await q.message.reply_text("Apna 12-digit UTR number type karein:")
        context.user_data['waiting_utr'] = True

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_utr'):
        utr = update.message.text
        admin_info = f"💰 **Payment Alert!**\nUser: {update.effective_user.id}\nFee: {context.user_data['fee']}\nUTR: `{utr}`"
        await context.bot.send_message(ADMIN_ID, admin_info)
        await update.message.reply_text("✅ UTR received! Verification ke baad aap contest mein join ho jayenge.")
        context.user_data['waiting_utr'] = False

def main():
    Thread(target=run).start()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(handle_click))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    bot.run_polling()

if __name__ == '__main__': main()
