import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
print(f"Keys -> BOT:{bool(BOT_TOKEN)} GROQ:{bool(GROQ_KEY)}")

app = Flask(__name__)

# Groq AI reply
def get_ai_reply(user_msg):
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Nuvu Nainu vi. Telugu English mix lo cool ga matladu."},
                {"role": "user", "content": user_msg}
            ]
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=15)
        j = r.json()
        print(f"Groq response: {j}")
        if "choices" not in j:
            return f"Groq Error bro: {j.get('error', j)} - Key check chey!"
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq Exception: {e}")
        return "Bro Groq busy, malli adugu! 😅"

# Send message to telegram
def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route('/')
def home():
    return "TheGroqaibot LIVE 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print(f"Update: {data}")
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            
            if text == "/start":
                send_telegram(chat_id, "Hey bro! Nenu Nainu AI! WEBHOOK tho LIVE ayya 🔥🔥🔥")
            else:
                reply = get_ai_reply(text)
                send_telegram(chat_id, reply)
    except Exception as e:
        print(f"Webhook error: {e}")
    return "ok", 200

# Auto set webhook on start
@app.route('/setwebhook')
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True"
    r = requests.get(url)
    return r.text

if __name__ == "__main__":
    # Set webhook automatically
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True", timeout=10)
        print("✅ Webhook set!")
    except:
        pass
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
