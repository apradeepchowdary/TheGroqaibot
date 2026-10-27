import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
app = Flask(__name__)

def get_btc_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr", timeout=10).json()
        usd = r['bitcoin']['usd']
        inr = r['bitcoin']['inr']
        return f"${usd:,} (₹{inr:,})"
    except:
        return None

def get_ai_reply(user_msg):
    low = user_msg.lower()

    # 1. BTC LIVE price
    if "bitcoin" in low or "btc" in low:
        price = get_btc_price()
        if price:
            return f"Yo bro! Bitcoin LIVE price: {price} 🚀 Ippudu market chudu bro!"

    # 2. News details adigithe hallucinate cheyaku
    if "more about this news" in low or "aa news gurinchi" in low:
        return "Bro naku live search ledu, forward chesina news meeda matrame matladagalanu bro. Nee opinion enti? 🤔"

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {
                    "role": "system",
                    "content": """You are GROQ AI.

                    RULES - VERY IMPORTANT:
                    1. You are GROQ AI only. If user asks 'nuvvu evaru?' say 'Nenu Groq AI ni bro!'.
                    2. ALWAYS reply in TELUGU written with ENGLISH LETTERS ONLY. Example: 'ela unnav bro?', 'emi chestunnav?', 'nenu Groq AI ni'. NEVER use Telugu script like 'ఏం'.
                    3. Mix 70% Telugu (in English letters) + 30% English. Short, cool, friendly.
                    4. Always call user 'bro'.
                    5. Don't guess live prices or news - if you don't know, say you don't have live search."""
                },
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.7,
            "max_tokens": 400
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=20)
        j = r.json()
        if "choices" in j:
            return j["choices"][0]["message"]["content"]
        else:
            print("Groq Error:", j)
            return "Bro koncham error vachindi, malli adugu bro! 😅"
    except Exception as e:
        print("Exception:", e)
        return "Bro busy ga unna, 1 nimisham tarvata adugu bro! 😅"

def send_telegram(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram send error:", e)

@app.route('/')
def home():
    return "GROQ AI BOT LIVE 🚀 - Telugish Mode"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        
        if text == "/start":
            send_telegram(chat_id, "Hey bro! Nenu Groq AI ni! 🔥 Naku emaina adugu - antha Telugish lo chepta bro!")
        else:
            reply = get_ai_reply(text)
            send_telegram(chat_id, reply)
    return "ok", 200

@app.route('/setwebhook')
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True"
    r = requests.get(url)
    return r.text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
