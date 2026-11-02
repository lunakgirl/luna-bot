import telebot
import config
import os
import gdown
from flask import Flask
from threading import Thread

bot = telebot.TeleBot(config.BOT_TOKEN)
ADMIN_ID = 7683621526

# IDS DO DRIVE
DRIVE = {
    "sonho": "1xaRU_FSu5esi-l_7Ii1ppGFrLUds9vtj",
    "sonho2": "1444QDpTtfE_PSeQpx49R18j2lgFy_bV3",
    "total": "1MacwPAL9GkSFGcJYvG2zlPXZmDxhqj2q",
    "videos": "1-v0bQOEOQlgWHWea8BRbtLG-y5qz7guQ"
}

# SONHO MANDA OS 2 JUNTOS!
PACKS = {
    "sonho": [DRIVE["sonho"], DRIVE["sonho2"]],
    "total": [DRIVE["total"]],
    "videos": [DRIVE["videos"]]
}

# SEUS LINKS DE PAGAMENTO (BravoPay / PagSeguroPix)
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

def teclado_inicial():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("🔥 QUERO O PACK SONHO - R$10", callback_data="pack_sonho"),
        telebot.types.InlineKeyboardButton("💦 QUERO O PACK TOTAL - R$25", callback_data="pack_total"),
        telebot.types.InlineKeyboardButton("🎥 QUERO OS VIDEOS - R$20", callback_data="pack_videos")
    )
    return markup

def teclado_pagamento(pack):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("💳 PASSO 1: CLIQUE AQUI PARA PAGAR", url=PAY.get(pack, "")),
        telebot.types.InlineKeyboardButton("📸 PASSO 2: JÁ PAGUEI, ENVIAR COMPROVANTE", callback_data=f"como_enviar_{pack}"),
        telebot.types.InlineKeyboardButton("⬅️ VOLTAR", callback_data="voltar_inicio")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    texto = (
        "Oi amor, sou a Luna 😏💦\n\n"
        "Tava te esperando aqui peladinha...\n\n"
        "👇 *CLIQUE EM UM BOTÃO ABAIXO PARA ESCOLHER:*"
    )
    bot.send_message(m.chat.id, texto, parse_mode="Markdown", reply_markup=teclado_inicial())

@bot.callback_query_handler(func=lambda c: True)
def botoes(c):
    try:
        bot.answer_callback_query(c.id)
    except:
        pass
    
    if c.data == "voltar_inicio":
        bot.edit_message_text(
            "Oi amor, sou a Luna 😏💦\n\n👇 *CLIQUE EM UM BOTÃO ABAIXO PARA ESCOLHER:*",
            c.message.chat.id, c.message.message_id,
            parse_mode="Markdown", reply_markup=teclado_inicial()
        )
        return

    if c.data.startswith("pack_"):
        pack = c.data.replace("pack_", "")
        aguardando[c.from_user.id] = pack
        
        textos = {
            "sonho": "🔥 *PACK SONHO - R$10*\n\nVocê vai me ver toda molhadinha, 2 packs juntos (sonho + continuação) 😈💦\n\n44 fotos + continuação bem putinha, seios, bundinha, toda molhadinha só pra você\n\n👇 *COMO COMPRAR (MUITO FÁCIL):*\n\n*PASSO 1:* Clique no botão VERDE abaixo *PAGAR*\n*PASSO 2:* Pague com Pix\n*PASSO 3:* Volte aqui e clique no botão *JÁ PAGUEI* e mande o print do comprovante",
            "total": "💦 *PACK TOTAL - R$25*\n\n66 fotos toda pelada, bem safada, nas posições que você mais gosta... 😏\n\n👇 *COMO COMPRAR:*\n\n*PASSO 1:* Clique no botão VERDE *PAGAR*\n*PASSO 2:* Pague\n*PASSO 3:* Clique em *JÁ PAGUEI* e mande o print",
            "videos": "🎥 *PACK VIDEOS - R$20*\n\n6 vídeos me tocando bem gostoso, gemendo seu nome, falando putaria pra você bater junto 🥵\n\n👇 *COMO COMPRAR:*\n\n*PASSO 1:* Clique em *PAGAR*\n*PASSO 2:* Pague\n*PASSO 3:* Clique em *JÁ PAGUEI* e mande o print"
        }
        
        bot.edit_message_text(
            textos.get(pack, ""), c.message.chat.id, c.message.message_id,
            parse_mode="Markdown", reply_markup=teclado_pagamento(pack)
        )
        return

    if c.data.startswith("como_enviar_"):
        bot.send_message(
            c.message.chat.id,
            "📸 *AGORA É FÁCIL:*\n\n1️⃣ Tira print do comprovante do Pix\n2️⃣ Clica no clips 📎 aqui embaixo\n3️⃣ Manda a foto do comprovante aqui\n\nAssim que meu dono ver, eu te mando na hora! 💦",
            parse_mode="Markdown"
        )
        return

    if c.data.startswith("ok:") or c.data.startswith("no:"):
        if c.from_user.id != ADMIN_ID:
            bot.answer_callback_query(c.id, "Só meu dono aprova 😏")
            return
        try:
            acao, uid, pack = c.data.split(":")
            uid = int(uid)
            if acao == "no":
                bot.send_message(uid, "❌ Amor, não consegui confirmar... manda o comprovante de novo bem nítido? Clica no clips 📎 e manda a foto 😢")
                try:
                    bot.edit_message_caption("❌ RECUSADO", chat_id=c.message.chat.id, message_id=c.message.message_id)
                except:
                    pass
                return
            
            bot.send_message(uid, "✅ *Aprovado amor!* Tô toda molhadinha te esperando... aqui está seu pack 😈💦", parse_mode="Markdown")
            for file_id in PACKS[pack]:
                out = f"/tmp/{file_id}.zip"
                if download_drive(file_id, out) and os.path.exists(out):
                    try:
                        with open(out, 'rb') as f:
                            bot.send_document(uid, f, caption=f"Seu {pack} amor... aproveita bem gostoso 😏💦")
                    except Exception as e:
                        print(f"Erro enviar: {e}")
                    try:
                        os.remove(out)
                    except:
                        pass
                else:
                    bot.send_message(ADMIN_ID, f"⚠️ Erro ao baixar {file_id} do Drive para {uid}")
            
            try:
                bot.edit_message_caption("✅ APROVADO", chat_id=c.message.chat.id, message_id=c.message.message_id)
            except:
                pass
            bot.send_message(ADMIN_ID, f"✅ Venda concluída: {pack} para {uid}")
        except Exception as e:
            print(f"Erro aprovar: {e}")
        return

@bot.message_handler(content_types=['photo', 'document'])
def comprovante(m):
    pack = aguardando.get(m.from_user.id)
    if not pack:
        bot.send_message(m.chat.id, "Amor, primeiro clica em um pack aqui 👇", reply_markup=teclado_inicial())
        return
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ APROVAR", callback_data=f"ok:{m.from_user.id}:{pack}"),
        telebot.types.InlineKeyboardButton("❌ RECUSAR", callback_data=f"no:{m.from_user.id}:{pack}")
    )
    caption = f"💰 Nova venda! Pack: {pack} Cliente: {m.from_user.id} @{m.from_user.username}"
    if m.content_type == 'photo':
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption, reply_markup=markup)
    else:
        bot.send_document(ADMIN_ID, m.document.file_id, caption=caption, reply_markup=markup)
    
    bot.send_message(m.chat.id, "📩 *Recebi seu comprovante amor!*\n\nJá mandei pro meu dono aprovar, em 2 minutinhos te mando peladinha aqui 💦\n\nFica de olho no chat 😘", parse_mode="Markdown")
    aguardando.pop(m.from_user.id, None)

# Flask pro Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Luna bot ta on 😏💦"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_flask).start()
print("Bot Luna iniciada")
bot.infinity_polling()
