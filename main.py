import os, requests, re
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
app = Flask(__name__)

def clean_text(t):
    t = re.sub(r'Rainbet\.com.*', '', t, flags=re.IGNORECASE|re.DOTALL)
    t = re.sub(r'http\S+|https\S+|t\.me/\S+|@\w+', '', t)
    t = re.sub(r'Forwarded from.*|BRICS News|War Monitor|Channel.*', '', t, flags=re.IGNORECASE)
    t = t.replace('⚡','').replace('💧','').replace('🔥','').replace('📰','').replace('JUST IN:','')
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:800]

def get_ai_reply(user_msg):
    clean = clean_text(user_msg)
    print(f"CLEAN: {clean}", flush=True)
    if len(clean) < 4:
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": "You are Groq AI. RULE: Reply ONLY in Telugish (Telugu in English letters). 3 lines max. Bro style, funny. Example: Kim Jong Un North Korea army ni combat ki ready avamannadu anta bro, tension perigindi. Never say English essay. Ads ignore. If asked who are you: Nenu Groq AI bro!"},
            {"role": "user", "content": clean}
        ],
        "temperature": 0.6,
        "max_tokens": 250
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"STATUS: {r.status_code}", flush=True)
        print(f"RAW: {r.text[:1000]}", flush=True)
        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            err = data.get("error", {}).get("message", "unknown")
            return f"Bro error: {err[:200]}"
    except Exception as e:
        print(f"EX: {e}", flush=True)
        return "Bro network issue, malli pampu bro!"

def send_telegram(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text})

@app.route('/')
def home():
    return "GROQ AI ON"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        msg = data.get("message") or data.get("channel_post") or data.get("edited_message") or data.get("edited_channel_post")
        if not msg:
            return "ok", 200
        chat_id = msg["chat"]["id"]
        text = msg.get("text") or msg.get("caption") or ""
        print(f"GOT: {text[:200]}", flush=True)
        if not text:
            return "ok", 200
        if text.strip() == "/start":
            send_telegram(chat_id, "Hey bro! 😎 Nenu ready! News forward chey - Telugish lo chepta!")
        else:
            reply = get_ai_reply(text)
            if reply:
                send_telegram(chat_id, reply)
    except Exception as e:
        print(f"WEBHOOK ERR: {e}", flush=True)
    return "ok", 200

@app.route('/setwebhook')
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True"
    r = requests.get(url)
    return r.text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
