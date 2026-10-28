import os, requests, re
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
app = Flask(__name__)

def clean_text(t):
    # Ads / links motham delete
    t = re.sub(r'Rainbet\.com.*', '', t, flags=re.IGNORECASE|re.DOTALL)
    t = re.sub(r'http\S+|https\S+|t\.me/\S+|@\w+', '', t)
    t = re.sub(r'Forwarded from.*|War Monitor|News \| Markets.*', '', t, flags=re.IGNORECASE)
    t = t.replace('⚡','').replace('💧','').replace('🔥','').replace('📰','')
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:800]

def get_ai_reply(user_msg):
    clean = clean_text(user_msg)
    print(f"CLEAN TEXT: {clean}", flush=True)
    if len(clean) < 4:
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are Groq AI. RULE: Reply ONLY in Telugish - Telugu words in English letters. No English essay. 3 lines max. Bro style. Example: Netanyahu bloc munduku vellindi anta bro, Eisenkot bloc kanna ekkuva vachindi Channel 12 poll lo. Ads ignore chey. If asked who are you: Nenu Groq AI bro!"},
            {"role": "user", "content": clean}
        ],
        "temperature": 0.6,
        "max_tokens": 250
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"GROQ STATUS: {r.status_code}", flush=True)
        print(f"GROQ RAW: {r.text[:1000]}", flush=True)
        
        data = r.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            err = data.get("error", {}).get("message", str(data)[:200])
            print(f"GROQ ERROR DETAILS: {err}", flush=True)
            # Key error ayina kuda Telugish lo cheppu, error message kadu
            return f"Bro Groq key lo problem undi: {err} - koncham check chey bro! Key expire ayyinda?"
            
    except Exception as e:
        print(f"EXCEPTION: {e}", flush=True)
        return "Bro koncham network issue, malli oka sari pampu bro!"

def send_telegram(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"SEND ERROR: {e}", flush=True)

@app.route('/')
def home():
    return "GROQ AI ON - Ready"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        msg = data.get("message") or data.get("channel_post") or data.get("edited_message") or data.get("edited_channel_post")
        if not msg:
            return "ok", 200
        chat_id = msg["chat"]["id"]
        text = msg.get("text") or msg.get("caption") or ""
        
        if not text:
            return "ok", 200
            
        print(f"GOT RAW: {text[:200]}", flush=True)
        
        if text.strip() == "/start":
            send_telegram(chat_id, "Hey bro! Nenu ready! 😎 News forward chey - ads lekunda Telugish lo chepta!")
        else:
            reply = get_ai_reply(text)
            if reply:
                send_telegram(chat_id, reply)
    except Exception as e:
        print(f"WEBHOOK ERROR: {e}", flush=True)
    return "ok", 200

@app.route('/setwebhook')
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True"
    r = requests.get(url)
    return r.text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
