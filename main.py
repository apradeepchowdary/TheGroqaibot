import os, requests, asyncio, threading, time
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

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
        data = {"model": "llama-3.3-70b-versatile","messages": [{"role": "system", "content": "Nuvu Nainu vi, cool Telugu English mix."},{"role": "user", "content": user_msg}]}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Bro busy unna, malli adugu! 😅"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey bro! Nenu Nainu AI! LIVE ayya! 🔥")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = get_ai_reply(update.message.text)
    await update.message.reply_text(reply)

async def run_bot_async():
    while True:
        try:
            print("Trying to connect to Telegram...")
            # Timeout ekkuva petta
            request = HTTPXRequest(connection_pool_size=8, connect_timeout=30, read_timeout=30, write_timeout=30, pool_timeout=30)
            application = Application.builder().token(BOT_TOKEN).request(request).build()
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
            
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            print("✅ Bot polling STARTED! Ready bro!")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"Bot connection failed: {e} - Retrying in 10 sec...")
            await asyncio.sleep(10)

def run_bot():
    asyncio.run(run_bot_async())

threading.Thread(target=run_bot, daemon=True).start()
