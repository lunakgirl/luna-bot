import telebot
import config
import os
import gdown

bot = telebot.TeleBot(config.BOT_TOKEN)

PACKS = {
    "sonho": "1xaRU_FSu5esi-l_7Ii1ppGFrLUds9vtj",
    "sonho2": "1444QDpTtfE_PSeQpx49R18j2lgFy_bV3",
    "total": "1MacwPAL9GkSFGcJYvG2zlPXZmDxhqj2q",
    "videos": "1-v0bQOEOQlgWHWea8BRbtLG-y5qz7guQ"
}

def download_from_drive(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output, quiet=False, fuzzy=True)
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Oi amor, sou a Luna 😏\n\nEscolhe:\n\n/sonho - R$ 10\n/sonho2 - R$ 15\n/total - R$ 25\n/videos - R$ 20")

@bot.message_handler(commands=['sonho', 'sonho2', 'total', 'videos'])
def handle_pack(message):
    pack_name = message.text.replace("/", "").lower()
    bot.reply_to(message, f"Gerando seu pack {pack_name}... ⏳")
    file_id = PACKS[pack_name]
    output_file = f"/tmp/{pack_name}.zip"
    if download_from_drive(file_id, output_file) and os.path.exists(output_file):
        with open(output_file, 'rb') as f:
            bot.send_document(message.chat.id, f)
        os.remove(output_file)
    else:
        bot.reply_to(message, "Erro no Drive, me chama no @")

bot.infinity_polling()
