import os
import requests
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

# Keys check
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
print(f"Keys -> BOT:{bool(BOT_TOKEN)} GROQ:{bool(GROQ_KEY)}")

app = Flask(__name__)

@app.route('/')
def home():
    return "TheGroqaibot Running! 🚀"

def get_ai_reply(user_msg):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Nuvu Nainu vi. Cool Telugu + English mix lo matladu. Short, friendly, funny replies ivvu. User ni bro ani piluvu."},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.7
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=20)
        print(f"Groq Status: {r.status_code}")
        j = r.json()
        
        if 'choices' not in j:
            print(f"Groq Full Response: {j}")
            return "Bro Groq key lo issue undi, key check chey! 😅"
            
        return j['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Bro konchem busy, malli adugu! 😅"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"/start from {update.effective_user.id}")
    await update.message.reply_text("Hey bro! Nenu Nainu AI bot ni! TheGroqaibot LIVE 🔥 Adugu em kavalo!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"User: {user_text}")
    reply = get_ai_reply(user_text)
    await update.message.reply_text(reply)

async def run_bot_async():
    while True:
        try:
            print("Trying to connect to Telegram...")
            request = HTTPXRequest(
                connection_pool_size=8,
                connect_timeout=30,
                read_timeout=30,
                write_timeout=30,
                pool_timeout=30
            )
            application = Application.builder().token(BOT_TOKEN).request(request).build()
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
            
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            print("✅ Bot polling STARTED! Ready bro!")
            await asyncio.Event().wait()
            
        except Exception as e:
            print(f"Bot failed: {e} - Retrying in 10 sec...")
            await asyncio.sleep(10)

def run_bot():
    asyncio.run(run_bot_async())

# Start bot in background
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
