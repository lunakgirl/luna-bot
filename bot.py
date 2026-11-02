import telebot
import config
import os
import gdown
from flask import Flask
from threading import Thread

bot = telebot.TeleBot(config.BOT_TOKEN)
ADMIN_ID = 7683621526

# DRIVE IDS
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

aguardando = {}

def download_drive(file_id, output):
    try:
        gdown.download(id=file_id, output=output, quiet=False)
        if os.path.exists(output):
            return True
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output, quiet=False, fuzzy=True)
        return os.path.exists(output)
    except Exception as e:
        print(f"Erro download {file_id}: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(m):
    texto = (
        "Oi amor, sou a Luna 😏💦\n\n"
        "Tava te esperando aqui peladinha...\n\n"
        "Escolhe o que você quer ver de mim hoje? 👇\n\n"
        "🔥 *SONHO* - R$10\n"
        "44 fotos + continuação juntas, bem putinha, seios, bundinha, toda molhadinha só pra você se deliciar 😈\n\n"
        "💦 *TOTAL* - R$25\n"
        "66 fotos, toda pelada, bem safada, nas posições que você mais gosta... gozando só de pensar em você 😏\n\n"
        "🎥 *VIDEOS* - R$20\n"
        "6 vídeos me tocando bem gostoso, gemendo seu nome, falando putaria pra você bater junto comigo 🥵\n\n"
        "Qual vai ser, amor? Me chama no /sonho /total /videos 😘"
    )
    bot.reply_to(m, texto, parse_mode="Markdown")

@bot.message_handler(commands=['sonho', 'total', 'videos'])
def handle_pack(m):
    pack = m.text.replace("/", "").lower()
    aguardando[m.from_user.id] = pack
    
    msgs = {
        "sonho": "Esse é meu preferido, amor... você vai me ver toda molhadinha, bem putinha só pra você 😈\n\nSão 2 packs juntos, minha continuação toda peladinha 💦\n\nPaga aqui embaixo e me manda o comprovante que eu te mando na hora 🔥",
        "total": "Você quer me ver TODA né safado? 66 fotos bem putinha, aberta, mostrando tudo que é seu 😏\n\nToda pelada, nas posições que você mais gosta...\n\nPaga aqui e me manda o comprovante que já vou te mandar peladinha 🥵",
        "videos": "Quer me ver gozando? 6 vídeos me tocando bem gostoso, gemendo seu nome, falando putaria pra você bater junto comigo 💦\n\nVai gozar muito vendo eu me tocar... Paga aqui e manda o comprovante amor 🔥"
    }
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("💳 Pagar no Pix - R$10" if pack=="sonho" else f"💳 Pagar no Pix", url=PAY.get(pack, "")))
    
    bot.reply_to(m, msgs.get(pack, ""), reply_markup=markup)

@bot.message_handler(content_types=['photo', 'document'])
def comprovante(m):
    pack = aguardando.get(m.from_user.id)
    if not pack:
        bot.reply_to(m, "Amor, escolhe um pack primeiro: /sonho /total /videos 😘")
        return
    
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
    
    bot.reply_to(m, "📩 Comprovante recebido amor! Assim que meu dono aprovar eu te mando toda peladinha aqui 💦😏")
    aguardando.pop(m.from_user.id, None)

@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok:", "no:")))
def aprovar(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "Só meu dono aprova 😏")
        return
    
    acao, uid, pack = c.data.split(":")
    uid = int(uid)
    
    if acao == "no":
        bot.send_message(uid, "❌ Amor, pagamento não confirmado... verifica e me manda de novo? 😢")
        bot.edit_message_caption("❌ RECUSADO", chat_id=c.message.chat.id, message_id=c.message.message_id)
        return
    
    bot.send_message(uid, "✅ Aprovado amor! Tô toda molhadinha te esperando... aqui está seu pack 😈💦")
    for file_id in PACKS[pack]:
        out = f"/tmp/{file_id}.zip"
        if download_drive(file_id, out) and os.path.exists(out):
            try:
                with open(out, 'rb') as f:
                    bot.send_document(uid, f, caption=f"Seu {pack} amor... aproveita bem gostoso de mim 😏💦")
            except Exception as e:
                print(f"Erro enviar: {e}")
            try:
                os.remove(out)
            except:
                pass
        else:
            bot.send_message(ADMIN_ID, f"⚠️ Erro ao baixar {file_id} do Drive para {uid}")
    
    bot.edit_message_caption("✅ APROVADO", chat_id=c.message.chat.id, message_id=c.message.message_id)
    bot.send_message(ADMIN_ID, f"✅ Venda concluída: {pack} para {uid}")

# Flask pro Render não dormir
app = Flask(__name__)
@app.route('/')
def home():
    return "Luna bot ta on 😏💦"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_flask).start()
bot.infinity_polling()
