import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
print(f"Keys -> BOT:{bool(BOT_TOKEN)} GROQ:{bool(GROQ_KEY)}")

app = Flask(__name__)

def get_ai_reply(user_msg):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "Nuvu Nainu vi, Vijayawada nundi. Telugu + English mix lo short, cool, friendly ga matladu. User ni bro ani piluvu."},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=20
        )
        j = r.json()
        print(f"Groq Status: {r.status_code} Response: {j}")
        
        if "choices" in j:
            return j["choices"][0]["message"]["content"]
        else:
            return f"Groq Error: {j.get('error', {}).get('message', j)}"
            
    except Exception as e:
        print(f"Groq Exception: {e}")
        return "Bro koncham busy unna, malli adugu! 😅"

def send_telegram(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

@app.route('/')
def home():
    return "TheGroqaibot LIVE 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print(f"Incoming: {data}")
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            
            if text == "/start":
                send_telegram(chat_id, "Hey bro! Nenu Nainu AI! LIVE ayya FINAL ga! 🔥 Adugu em kavalo?")
            else:
                reply = get_ai_reply(text)
                send_telegram(chat_id, reply)
    except Exception as e:
        print(f"Webhook error: {e}")
    return "ok", 200

@app.route('/setwebhook')
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True"
    r = requests.get(url)
    return r.text

if __name__ == "__main__":
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True", timeout=10)
        print("✅ Webhook set!")
    except:
        pass
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
