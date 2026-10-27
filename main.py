import os
from flask import Flask
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

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
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Nuvu Nainu vi. Cool Telugu + English mix lo matladu. Short, friendly, funny replies ivvu. User ni bro ani piluvu."},
                {"role": "user", "content": user_msg}
            ]
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=15)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return "Bro konchem busy, malli adugu! 😅"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey bro! Nenu Nainu AI bot ni! Adugu em kavalo! 🔥")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"User: {user_text}")
    reply = get_ai_reply(user_text)
    await update.message.reply_text(reply)

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    application.run_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
