import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")
app = Flask(__name__)

def search_live(query):
    if not TAVILY_KEY or len(query) < 10:
        return None
    try:
        r = requests.post("https://api.tavily.com/search", json={
            "api_key": TAVILY_KEY,
            "query": query,
            "max_results": 3,
            "include_answer": True
        }, timeout=15).json()
        txt = ""
        for x in r.get("results", [])[:2]:
            txt += x.get("content","")[:400] + " "
        return txt or r.get("answer")
    except:
        return None

def get_btc_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr", timeout=10).json()
        return f"${r['bitcoin']['usd']:,} (₹{r['bitcoin']['inr']:,})"
    except: return None

def get_ai_reply(user_msg):
    low = user_msg.lower()
    extra = ""
    
    if "btc" in low or "bitcoin" in low:
        p = get_btc_price()
        if p: extra += f" LIVE BTC Price = {p}. "
    
    # News aithe live search
    if len(user_msg) > 15:
        live = search_live(user_msg[:250])
        if live: extra += f" LIVE INFO: {live} "

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    system_prompt = f"""You are GROQ AI.

    ULTRA STRICT RULES - BREAK CHEYAKU:
    1. You are GROQ AI. If asked 'nuvvu evaru?' say 'Nenu Groq AI ni bro!'
    2. EVERY WORD YOU WRITE MUST BE TELUGU IN ENGLISH LETTERS. No full English sentences. 
    3. Example style: 'Brazil lo election roju companies stablecoin konnayi bro, currency padakunda undataniki, safe plan bro idhi'
    4. If you explain a word, explain in Telugish only: 'Stablecoin ante dollar ki fix ayina crypto bro, value taggadu'
    5. NEVER write like 'crypto asset that's pegged to a fiat'. NEVER.
    6. Keep reply 4-5 lines max, cool bro style.
    7. Use this live data: {extra}
    8. Never say 'live ledu' - you have live data.
    """

    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=25).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        print(e)
        return "Bro koncham error vachindi, malli pampu bro!"

def send_telegram(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text})

@app.route('/')
def home(): return "GROQ AI - Full Telugish + Live ON"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return "ok", 200
    msg = data.get("message") or data.get("channel_post") or data.get("edited_message")
    if not msg: return "ok", 200
    
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text") or msg.get("caption") or ""
    
    if text and chat_id:
        text = text.replace("News | Markets | YouTube", "").strip()
        if text == "/start":
            send_telegram(chat_id, "Hey bro! Nenu Groq AI ni! Ippudu full Telugish lo, LIVE search tho chepta bro! Emaina forward chey!")
        else:
            send_telegram(chat_id, get_ai_reply(text))
    return "ok", 200

@app.route('/setwebhook')
def set_webhook():
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True")
    return r.text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
