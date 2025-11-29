from telegram import Update
from telegram.ext import Application, MessageHandler, filters , ContextTypes, CommandHandler, ChatMemberHandler

from handlers.rewards import manejar_imagenes
from handlers.welcoming import nuevo_usuario,mensaje_de_presentaciones
from handlers.general import dar,ver,regalar,numero_azar,quitar # type: ignore
from handlers.theme_juegosYcasino import apostar,aceptar,detectar_dado,cancelar_apuesta,jugar,robar

from config import BOT_TOKEN # type: ignore

async def get_theme_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        thread_id = update.message.message_thread_id
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            f"📌 Chat ID: `{chat_id}`\n"
            f"📌 Theme (message_thread_id): `{thread_id}`",
            parse_mode="Markdown"
        )
async def saludar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_bienvenida = (
        "🎄✨ *¡Ho, ho, ho! Llegó PiBot al chat* ✨🎄\n"
        "¡Hola a todos! 🤖🎅\n"
        "Estoy aquí para traer *alegría, buena vibra y espíritu navideño* a este lugar.\n"
        "Prepárense para luces, diversión y un montón de sorpresas festivas. 🎁❄️\n\n"
        "¡Que comience la magia navideña! 🎅🤖✨"
    )
    await update.message.reply_text(mensaje_bienvenida, parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    filtro_imagen = filters.PHOTO | filters.Document.IMAGE
    
    # Handlers recompensas
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, manejar_imagenes))


    # Handler general (para todos los chats)
    app.add_handler(CommandHandler("ver", ver))
    app.add_handler(CommandHandler("regalar", regalar))
    app.add_handler(CommandHandler("dar", dar))
    app.add_handler(CommandHandler("quitar", quitar))
    app.add_handler(CommandHandler("NumAzar", numero_azar))
    app.add_handler(CommandHandler("id", get_theme_id))
    app.add_handler(CommandHandler("saludar", saludar))
    
    # Handlers de bienvenida
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, nuevo_usuario))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_de_presentaciones))
    
    # Handlers juegos
    app.add_handler(CommandHandler("apostar", apostar))
    app.add_handler(CommandHandler("aceptar", aceptar))
    app.add_handler(CommandHandler("cancelar", cancelar_apuesta))
    app.add_handler(CommandHandler("jugar", jugar))
    app.add_handler(CommandHandler("robar", robar))
    app.add_handler(MessageHandler(filters.Dice.ALL, detectar_dado))

    
    print("🤖 Bot corriendo...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()