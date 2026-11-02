import telebot
import config
import os
import gdown
from flask import Flask
from threading import Thread

bot = telebot.TeleBot(config.BOT_TOKEN)
ADMIN_ID = 7683621526

# DRIVE
DRIVE = {
    "sonho": "1xaRU_FSu5esi-l_7Ii1ppGFrLUds9vtj",
    "sonho2": "1444QDpTtfE_PSeQpx49R18j2lgFy_bV3",
    "total": "1MacwPAL9GkSFGcJYvG2zlPXZmDxhqj2q",
    "videos": "1-v0bQOEOQlgWHWea8BRbtLG-y5qz7guQ"
}

# sonho manda os 2 juntos!
PACKS = {
    "sonho": [DRIVE["sonho"], DRIVE["sonho2"]],
    "total": [DRIVE["total"]],
    "videos": [DRIVE["videos"]]
}

PAY = {
    "sonho": "https://pagseguropix.org/c/sonho",
    "total": "https://pagseguropix.org/c/packhard",
    "videos": "https://pagseguropix.org/c/packs-videos-78x2"
}

# quem tá esperando comprovante
aguardando = {}

def download_drive(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output, quiet=False, fuzzy=True)
        return True
    except:
        return False

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Oi amor sou a Luna 😏\n\n/sonho - Sonho + Sonho2 juntos\n/total - 66 fotos\n/videos - 6 videos")

@bot.message_handler(commands=['sonho', 'total', 'videos'])
def handle_pack(m):
    pack = m.text.replace("/", "").lower()
    aguardando[m.from_user.id] = pack
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("💳 Pagar no Pix", url=PAY.get(pack, "")))
    bot.reply_to(m, f"Pack {pack} - Paga no link e depois MANDA O COMPROVANTE aqui (print) 👇", reply_markup=markup)

@bot.message_handler(content_types=['photo', 'document'])
def comprovante(m):
    pack = aguardando.get(m.from_user.id)
    if not pack:
        bot.reply_to(m, "Escolhe um pack antes: /sonho /total /videos")
        return
    
    # Manda pro admin aprovar
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Aprovar", callback_data=f"ok:{m.from_user.id}:{pack}"),
        telebot.types.InlineKeyboardButton("❌ Recusar", callback_data=f"no:{m.from_user.id}:{pack}")
    )
    
    caption = f"💰 Nova venda!\nPack: {pack}\nCliente: {m.from_user.id} @{m.from_user.username}"
    
    if m.content_type == 'photo':
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption, reply_markup=markup)
    else:
        bot.send_document(ADMIN_ID, m.document.file_id, caption=caption, reply_markup=markup)
    
    bot.reply_to(m, "📩 Comprovante recebido! Aguarde aprovação.")
    aguardando.pop(m.from_user.id, None)

@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok:", "no:")))
def aprovar(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "Só admin pode aprovar")
        return
    
    acao, uid, pack = c.data.split(":")
    uid = int(uid)
    
    if acao == "no":
        bot.send_message(uid, "❌ Pagamento não confirmado. Verifica e manda de novo.")
        bot.edit_message_caption("❌ RECUSADO", chat_id=c.message.chat.id, message_id=c.message.message_id)
        return
    
    # APROVADO - manda os packs do Drive
    bot.send_message(uid, "✅ Pagamento aprovado! Aqui está seu conteúdo:")
    for file_id in PACKS[pack]:
        out = f"/tmp/{file_id}.zip"
        if download_drive(file_id, out) and os.path.exists(out):
            with open(out, 'rb') as f:
                bot.send_document(uid, f)
            os.remove(out)
    
    bot.edit_message_caption("✅ APROVADO", chat_id=c.message.chat.id, message_id=c.message.message_id)
    bot.send_message(ADMIN_ID, f"✅ Venda concluída: {pack} para {uid}")

# Flask pro Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Luna bot ta on 😏"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_flask).start()
bot.infinity_polling()
