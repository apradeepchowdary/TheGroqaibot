import os, requests, asyncio, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
print(f"Keys -> BOT:{bool(BOT_TOKEN)} GROQ:{bool(GROQ_KEY)}")

app = Flask(__name__)
@app.route('/')
def home():
    return "TheGroqaibot Running! 🚀"

def get_ai_reply(user_msg):
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile","messages": [{"role": "system", "content": "Nuvu Nainu vi. Cool Telugu English mix, short funny."},{"role": "user", "content": user_msg}]}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return "Bro busy, malli adugu 😅"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"START from {update.effective_user.id}")
    await update.message.reply_text("Hey bro! Nenu Nainu AI! LIVE ayya! 🔥")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = get_ai_reply(update.message.text)
    await update.message.reply_text(reply)

async def run_bot_async():
    print("Bot polling starting...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    print("Bot polling STARTED!")
    await asyncio.Event().wait()

def run_bot():
    asyncio.run(run_bot_async())

threading.Thread(target=run_bot, daemon=True).start()
