import os, logging
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
import config
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID","0") or 0)
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID","")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
aguardando = {}
def preco_fmt(c): return f"R$ {c/100:.2f}".replace(".",",")
def teclado_catalogo():
    botoes = [[InlineKeyboardButton(f"{p['nome']} - {preco_fmt(p['preco_centavos'])}", callback_data=f"pack:{p['id']}")] for p in config.PACKS]
    botoes.append([InlineKeyboardButton("📢 Canal de Previas", callback_data="previas")])
    return InlineKeyboardMarkup(botoes)
async def enviar_convite(context, chat_id, uid):
    if not VIP_CHANNEL_ID: return
    try:
        link = await context.bot.create_chat_invite_link(chat_id=int(VIP_CHANNEL_ID), member_limit=1, name=f"previa-{uid}")
        await context.bot.send_message(chat_id, "📢 Canal de Previas\nEntre para ver previas gratis!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Entrar no canal", url=link.invite_link)]]))
    except Exception as e: log.error(e)
async def start(update, context):
    if context.args:
        arg = context.args[0]
        pack = next((p for p in config.PACKS if p["id"]==arg), None)
        if pack: context.user_data["pack_direto"]=pack["id"]
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Tenho 18+", callback_data="age_ok")],[InlineKeyboardButton("Sou menor", callback_data="age_no")]])
    await update.message.reply_text(config.TEXTO_18, reply_markup=kb)
async def on_callback(update, context):
    q = update.callback_query; await q.answer(); data = q.data
    if data=="age_no": await q.edit_message_text("🔞 Apenas +18"); return
    if data in ("age_ok","back_catalog"):
        await q.edit_message_text(config.TEXTO_BEMVINDO, reply_markup=teclado_catalogo())
        await enviar_convite(context, q.message.chat_id, q.from_user.id)
        pack_id = context.user_data.pop("pack_direto", None)
        if pack_id and data=="age_ok":
            pack = next((p for p in config.PACKS if p["id"]==pack_id), None)
            if pack:
                aguardando[q.from_user.id]=pack_id
                texto = f"*{pack['nome']}*\n{pack['descricao']}\nValor: *{preco_fmt(pack['preco_centavos'])}*"
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Pagar agora", url=pack["link_pagamento"])],[InlineKeyboardButton("Voltar", callback_data="back_catalog")]])
                await q.message.reply_text(texto, parse_mode="Markdown", reply_markup=kb)
        return
    if data=="previas": await enviar_convite(context, q.message.chat_id, q.from_user.id); return
    if data.startswith("pack:"):
        pack_id=data.split(":",1)[1]; pack=next((p for p in config.PACKS if p["id"]==pack_id),None)
        if not pack: return
        aguardando[q.from_user.id]=pack_id
        texto = f"*{pack['nome']}*\n{pack['descricao']}\nValor: *{preco_fmt(pack['preco_centavos'])}*"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Pagar agora", url=pack["link_pagamento"])],[InlineKeyboardButton("Voltar", callback_data="back_catalog")]])
        await q.edit_message_text(texto, parse_mode="Markdown", reply_markup=kb); return
    if data.startswith(("ok:","no:")):
        if q.from_user.id!=ADMIN_CHAT_ID: await q.answer("Apenas admin", show_alert=True); return
        acao,uid_str,pack_id=data.split(":",2); uid=int(uid_str)
        pack=next((p for p in config.PACKS if p["id"]==pack_id),None)
        if acao=="no":
            await context.bot.send_message(uid, config.TEXTO_RECUSADO); await q.edit_message_caption(caption=q.message.caption+"\nRECUSADO"); return
        await context.bot.send_message(uid, config.TEXTO_APROVADO)
        for arq in (pack["arquivos"] if pack else []):
            try:
                with open(arq,"rb") as f: await context.bot.send_document(uid, f)
            except FileNotFoundError: log.error(f"Arquivo nao encontrado: {arq}")
        await q.edit_message_caption(caption=q.message.caption+"\nAPROVADO")
        await context.bot.send_message(ADMIN_CHAT_ID, f"Venda: {pack['nome'] if pack else pack_id} para {uid}")
async def on_receipt(update, context):
    uid=update.message.from_user.id; pack_id=aguardando.get(uid)
    if not pack_id: await update.message.reply_text("Envie /start e escolha um pack antes."); return
    pack=next((p for p in config.PACKS if p["id"]==pack_id),None)
    legenda=f"Nova venda\nPack: {pack['nome'] if pack else pack_id}\nValor: {preco_fmt(pack['preco_centavos']) if pack else '?'}\nCliente: {uid}"
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("Aprovar", callback_data=f"ok:{uid}:{pack_id}"), InlineKeyboardButton("Recusar", callback_data=f"no:{uid}:{pack_id}")]])
    msg=update.message
    if msg.photo: await context.bot.send_photo(ADMIN_CHAT_ID, msg.photo[-1].file_id, caption=legenda, reply_markup=kb)
    elif msg.document: await context.bot.send_document(ADMIN_CHAT_ID, msg.document.file_id, caption=legenda, reply_markup=kb)
    else: return
    aguardando.pop(uid,None); await msg.reply_text(config.TEXTO_COMPROVANTE_RECEBIDO)
def main():
    if not BOT_TOKEN: raise SystemExit("Configure BOT_TOKEN no .env")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, on_receipt))
    log.info("Bot rodando..."); app.run_polling()
if __name__=="__main__": main()
