import os, requests, re
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
app = Flask(__name__)

def clean_text(t):
    # Ad links, @mentions clean chey
    t = re.sub(r'Rainbet\.com.*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'@\w+', '', t)
    t = t.replace("Forwarded from", "").strip()
    return t[:1000] # pedda news ayina cut chey

def get_ai_reply(user_msg):
    try:
        clean = clean_text(user_msg)
        if len(clean) < 3: return None
        
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        system_prompt = """
        You are GROQ AI. STRICT RULES:
        1. You MUST reply ONLY in Telugish (Telugu words written in English letters). 
        2. NEVER reply in full English. Never write paragraph essay.
        3. Example: 'US election site ni hacker kodtunnadu anta bro, FEC official mail ni Reuters chusindi, tension scene bro idhi'
        4. Reply 3-4 lines max, bro style. No ** bold, no headings.
        5. If user says 'nuvvu evaru' say 'Nenu Groq AI bro!'
        """

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": clean}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=20)
        j = r.json()
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"GROQ ERROR: {e}")
        return "Bro error vachindi, malli pampu, nenu Telugish lone chepta bro!"

def send_telegram(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"SEND ERROR: {e}")

@app.route('/')
def home(): return "GROQ AI ON - Telugish Only"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        msg = data.get("message") or data.get("channel_post") or data.get("edited_message") or data.get("edited_channel_post")
        if not msg: return "ok", 200
        chat_id = msg["chat"]["id"]
        text = msg.get("text") or msg.get("caption") or ""
        if text:
            print(f"Got: {text[:100]}")
            if text.strip() == "/start":
                send_telegram(chat_id, "Hey bro lechanu! 😎 Ippudu full Telugish lo chepta! News forward chey!")
            else:
                reply = get_ai_reply(text)
                if reply:
                    send_telegram(chat_id, reply)
    except Exception as e:
        print(f"WEBHOOK ERROR: {e}")
    return "ok", 200

@app.route('/setwebhook')
def set_webhook():
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://thegroqaibot.onrender.com/webhook&drop_pending_updates=True")
    return r.text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
