import telebot
import config
import os
import gdown
from flask import Flask
from threading import Thread

bot = telebot.TeleBot(config.BOT_TOKEN)
ADMIN_ID = 7683621526

DRIVE = {
    "sonho": "1xaRU_FSu5esi-l_7Ii1ppGFrLUds9vtj",
    "sonho2": "1444QDpTtfE_PSeQpx49R18j2lgFy_bV3",
    "total": "1MacwPAL9GkSFGcJYvG2zlPXZmDxhqj2q",
    "videos": "1-v0bQOEOQlgWHWea8BRbtLG-y5qz7guQ"
}

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
        return os.path.exists(output)
    except:
        return False

# 3 BOTÕES, 1 PRA CADA PACK
def teclado_inicial():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("🔥 PACK SONHO - R$10 (2 EM 1)", callback_data="pack_sonho"),
        telebot.types.InlineKeyboardButton("💦 PACK TOTAL - R$25 (66 FOTOS)", callback_data="pack_total"),
        telebot.types.InlineKeyboardButton("🎥 PACK VIDEOS - R$20 (6 VIDEOS)", callback_data="pack_videos")
    )
    return markup

def teclado_pagamento(pack):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("💳 PASSO 1: CLICAR AQUI PARA PAGAR", url=PAY.get(pack, "")),
        telebot.types.InlineKeyboardButton("📸 PASSO 2: JÁ PAGUEI - ENVIAR COMPROVANTE", callback_data=f"como_{pack}"),
        telebot.types.InlineKeyboardButton("⬅️ VOLTAR", callback_data="voltar")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    texto = (
        "Oi amor, sou a Luna 😏💦\n\n"
        "Tava te esperando peladinha aqui...\n\n"
        "👇 *ESCOLHE O PACK CLICANDO NO BOTÃO:*"
    )
    bot.send_message(m.chat.id, texto, parse_mode="Markdown", reply_markup=teclado_inicial())

@bot.callback_query_handler(func=lambda c: True)
def botoes(c):
    try: bot.answer_callback_query(c.id)
    except: pass

    if c.data == "voltar":
        bot.edit_message_text(
            "Oi amor, sou a Luna 😏💦\n\n👇 *ESCOLHE O PACK:*",
            c.message.chat.id, c.message.message_id,
            parse_mode="Markdown", reply_markup=teclado_inicial()
        )
        return

    if c.data.startswith("pack_"):
        pack = c.data.replace("pack_", "")
        aguardando[c.from_user.id] = pack

        if pack == "sonho":
            desc = (
                "🔥 *PACK SONHO - R$10*\n"
                "_(2 EM 1 - SONHO + SONHO 2 JUNTOS)_\n\n"
                "📸 80+ fotos peladinha\n"
                "😈 Seios, bundinha, toda molhadinha\n"
                "💦 Nu artístico + bem putinha\n"
                "😏 Posições que você ama\n\n"
                "Esse é meu preferido amor, você vai ver tudo de mim bem molhadinha só pra você...\n\n"
                "👇 *COMO COMPRAR:*\n"
                "1️⃣ Clique em *PAGAR* abaixo\n"
                "2️⃣ Pague no Pix\n"
                "3️⃣ Clique em *JÁ PAGUEI* e mande o print"
            )
        elif pack == "total":
            desc = (
                "💦 *PACK TOTAL - R$25*\n"
                "_66 FOTOS_\n\n"
                "📸 66 fotos toda pelada\n"
                "🥵 Bem safada, aberta, mostrando tudo\n"
                "😏 Posições bem putinha do jeito que você gosta\n"
                "💦 Gozando só de pensar em você\n\n"
                "Quer me ver TODA né safado? Tudo que é seu...\n\n"
                "👇 *COMO COMPRAR:*\n"
                "1️⃣ Clique em *PAGAR*\n"
                "2️⃣ Pague\n"
                "3️⃣ Clique em *JÁ PAGUEI* e mande o print"
            )
        else: # videos
            desc = (
                "🎥 *PACK VIDEOS - R$20*\n"
                "_6 VIDEOS EXCLUSIVOS_\n\n"
                "🎬 6 vídeos me tocando\n"
                "🥵 Me masturbando bem gostoso\n"
                "😈 Gemendo seu nome\n"
                "💦 Falando putaria pra você bater junto\n\n"
                "Quer me ver gozando amor? Vai gozar junto comigo...\n\n"
                "👇 *COMO COMPRAR:*\n"
                "1️⃣ Clique em *PAGAR*\n"
                "2️⃣ Pague\n"
                "3️⃣ Clique em *JÁ PAGUEI* e mande o print"
            )

        bot.edit_message_text(desc, c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=teclado_pagamento(pack))
        return

    if c.data.startswith("como_"):
        bot.send_message(c.message.chat.id, "📸 *ENVIO DO COMPROVANTE:*\n\n1️⃣ Tira print do Pix\n2️⃣ Clica no clips 📎 aqui embaixo\n3️⃣ Manda a foto aqui\n\nJá vou te mandar peladinha 💦", parse_mode="Markdown")
        return

    if c.data.startswith("ok:") or c.data.startswith("no:"):
        if c.from_user.id != ADMIN_ID: return
        acao, uid, pack = c.data.split(":")
        uid = int(uid)
        if acao == "no":
            bot.send_message(uid, "❌ Amor, não confirmei... manda o comprovante de novo bem nítido? Clica no 📎 e manda a foto 😢")
            return
        bot.send_message(uid, "✅ *Aprovado amor!* Aqui está seu pack 😈💦", parse_mode="Markdown")
        for fid in PACKS[pack]:
            out = f"/tmp/{fid}.zip"
            if download_drive(fid, out) and os.path.exists(out):
                with open(out, 'rb') as f:
                    bot.send_document(uid, f)
                os.remove(out)
        try: bot.edit_message_caption("✅ APROVADO", chat_id=c.message.chat.id, message_id=c.message.message_id)
        except: pass
        return

@bot.message_handler(content_types=['photo', 'document'])
def comp(m):
    pack = aguardando.get(m.from_user.id)
    if not pack:
        bot.send_message(m.chat.id, "Clica em um pack primeiro amor 👇", reply_markup=teclado_inicial())
        return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ APROVAR", callback_data=f"ok:{m.from_user.id}:{pack}"),
        telebot.types.InlineKeyboardButton("❌ RECUSAR", callback_data=f"no:{m.from_user.id}:{pack}")
    )
    cap = f"💰 Nova venda! Pack: {pack} Cliente: {m.from_user.id}"
    if m.content_type == 'photo':
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=cap, reply_markup=markup)
    else:
        bot.send_document(ADMIN_ID, m.document.file_id, caption=cap, reply_markup=markup)
    bot.send_message(m.chat.id, "📩 Recebi amor! Assim que aprovar te mando peladinha 💦", parse_mode="Markdown")
    aguardando.pop(m.from_user.id, None)

app = Flask(__name__)
@app.route('/')
def home(): return "Luna bot ta on 😏"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_flask).start()
bot.infinity_polling()
