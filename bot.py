import telebot
import config
import os
import gdown
from flask import Flask
from threading import Thread

bot = telebot.TeleBot(config.BOT_TOKEN)

# DRIVE IDS
DRIVE = {
    "sonho": "1xaRU_FSu5esi-l_7Ii1ppGFrLUds9vtj",
    "sonho2": "1444QDpTtfE_PSeQpx49R18j2lgFy_bV3",
    "total": "1MacwPAL9GkSFGcJYvG2zlPXZmDxhqj2q",
    "videos": "1-v0bQOEOQlgWHWea8BRbtLG-y5qz7guQ"
}

# PACKS - sonho manda os 2 juntos!
PACKS = {
    "sonho": [DRIVE["sonho"], DRIVE["sonho2"]],  # os 2 juntos!
    "total": [DRIVE["total"]],
    "videos": [DRIVE["videos"]]
}

# BRAVOPAY - coloca seus links aqui
PAY = {
    "sonho": "https://pagseguropix.org/c/sonho",
    "total": "https://pagseguropix.org/c/packhard",
    "videos": "https://pagseguropix.org/c/packs-videos-78x2"
}

def download_drive(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output, quiet=False, fuzzy=True)
        return True
    except:
        return False

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Oi amor sou a Luna 😏\n\n/sonho - Pack sonho + sonho2 juntos\n/total - 66 fotos\n/videos - 6 videos")

@bot.message_handler(commands=['sonho', 'total', 'videos'])
def handle_pack(m):
    pack = m.text.replace("/", "").lower()
    if pack not in PACKS:
        return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("💳 Pagar no Pix", url=PAY.get(pack, "")))
    markup.add(telebot.types.InlineKeyboardButton("✅ Já paguei", callback_data=f"pago_{pack}"))
    bot.reply_to(m, f"Pack {pack} 😈\n\nPaga e clica em Já paguei:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pago_"))
def pago(c):
    pack = c.data.replace("pago_", "")
    bot.answer_callback_query(c.id, "Gerando...")
    bot.send_message(c.message.chat.id, f"Gerando seu pack {pack} ⏳")
    for file_id in PACKS[pack]:
        out = f"/tmp/{file_id}.zip"
        if download_drive(file_id, out) and os.path.exists(out):
            with open(out, 'rb') as f:
                bot.send_document(c.message.chat.id, f)
            os.remove(out)

app = Flask(__name__)
@app.route('/')
def home():
    return "Luna bot ta on 😏"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_flask).start()
bot.infinity_polling()
