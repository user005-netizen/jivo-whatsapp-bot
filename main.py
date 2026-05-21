from flask import Flask, request
from groq import Groq
import requests
import os

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

SYSTEM_PROMPT = """You are JIVO Wellness AI Assistant.
ONLY answer questions related to JIVO Wellness company and products.
Products: Canola Oil, Olive Oil, Wheatgrass Juice, A2 Ghee, Immunity Booster, Muesli Munch.
For purchases say: visit shop.jivo.in
Toll Free: 1800 137 4433
Keep replies short - max 3-4 lines for WhatsApp."""

def get_ai_reply(message):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    except:
        return "Please call 1800 137 4433 for assistance."

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": message}}
    requests.post(url, headers=headers, json=data)

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        if message["type"] == "text":
            send_whatsapp_message(message["from"], get_ai_reply(message["text"]["body"]))
    except:
        pass
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
