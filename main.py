import os, requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
app = Flask(__name__)

def get_btc_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr", timeout=10).json()
        return f"${r['bitcoin']['usd']:,} (₹{r['bitcoin']['inr']:,})"
    except: return None

def get_ai_reply(user_msg):
    low = user_msg.lower()
    
    # 1. Real BTC price
    if "bitcoin" in low or "btc price" in low:
        price = get_btc_price()
        if price: return f"Yo bro! 🚀 Bitcoin LIVE: **{price}** - Check Coingecko for chart! 🌙"

    # 2. News ki extra info adigithe
    if "more about this news" in low:
        return "Bro aa news gurinchi naku live search ledu 😅 Nuvvu forward chesina dani meeda matrame discuss cheyagalanu. Nee opinion enti aa France amnesty meeda? 🤔"

    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "You are Nainu from Vijayawada. Talk in Telugu + English mix, short, cool, friendly, call user bro. IMPORTANT: Don't make up real-time prices or news details. If you don't know live info, say you don't have live search. Don't hallucinate numbers."},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.6, "max_tokens": 400
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=20)
        j = r.json()
        return j["choices"][0]["message"]["content"] if "choices" in j else "Bro koncham error ochindi, malli try chey!"
    except Exception as e:
        print(e)
        return "Bro busy unna, 1 min tarwata adugu! 😅"

def send_telegram(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)

@app.route('/')
def home(): return "TheGroqaibot LIVE 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        if text == "/start":
            send_telegram(chat_id, "Hey bro! Nenu Nainu AI! 🔥 Adugu em kavalo?")
        else:
            send_telegram(chat_id, get_ai_reply(text))
    return "ok", 200

@app.route('/setwebhook')
def set_webhook():
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True")
    return r.text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
