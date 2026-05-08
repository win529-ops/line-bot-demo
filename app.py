from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, StickerMessage,
    TextSendMessage
)
import os
import random
from datetime import datetime, timedelta, timezone


app = Flask(__name__)

# 從 Render 環境變數讀取 LINE Bot 金鑰
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# --- 回覆模板 ---
reply_templates = {
    "text_blessing": [
        "早安，祝你今天心情愉快",
        "新的一天開始了，平安喜樂",
        "早安，願你今天充滿活力"
    ],
    "flowers_scenery": [
        "早安，好美的風景，祝你一天好心情",
        "花香伴隨早晨，祝福滿滿",
        "早安，景色真美，願你一天順心"
    ],
    "coffee_breakfast": [
        "早安，早餐很豐盛，祝你活力滿滿",
        "早安，咖啡香氣四溢，精神滿滿",
        "早安，享受美味早餐，幸福一天"
    ],
    "festival": [
        "早安，佳節快樂，平安喜樂",
        "早安，祝你節日愉快",
        "早安，佳節平安，幸福滿滿"
    ]
}

emoji_list = ["😊", "🌸", "☀️", "🌹", "🍵", "🍞", "🎉", "❤️"]

def get_time_period():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)
    hour = now.hour

    if 5 <= hour < 11:
        return "morning"
    elif 11 <= hour < 17:
        return "noon"
    else:
        return "evening"

def generate_reply(image_category):
    time_period = get_time_period()
    time_greetings = {
        "morning": "早安",
        "noon": "午安",
        "evening": "晚安"
    }
    if image_category in reply_templates:
        reply = random.choice(reply_templates[image_category])
    else:
        reply = "早安，祝你一天愉快"
    reply = f"{time_greetings[time_period]}，{reply} {random.choice(emoji_list)}"
    return reply

# --- LINE Webhook ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello, World")
    )

# 圖片訊息事件（早安圖）
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # TODO: 這裡可以接上 OCR/分類，目前先假設是早餐圖片
    image_category = "coffee_breakfast"
    reply_text = generate_reply(image_category)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# 貼圖訊息事件
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="早安，收到可愛的貼圖！😊")
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
