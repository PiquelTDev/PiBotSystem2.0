from telegram import ChatPermissions, Update
from telegram.ext import Application, MessageHandler, filters , ContextTypes, CommandHandler,CallbackQueryHandler

from handlers.rewards import manejar_imagenes
from handlers.welcoming import nuevo_usuario,mensaje_de_presentaciones
from handlers.general import dar,ver,regalar,numero_azar,quitar,get_receptor
from handlers.theme_juegosYcasino import apostar,aceptar,detectar_dado,cancelar_apuesta,jugar,robar
from handlers.starting_menu import start,menu_callback
from handlers.tienda import tienda,tienda_callback
from config import BOT_TOKEN, DOMS, obtener_temas_por_comunidad

USUARIOS_CASTIGADOS = {}

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
async def castigar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    actor_id = update.effective_user.id
    if chat_id != -1003397946543:
        await update.message.reply_text("❌ Este comando no está habilitado en este grupo.")
        return
    
    if actor_id not in DOMS:
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return
    
    usuario_objetivo = await get_receptor(update,context,2)
    if usuario_objetivo is False:
        return
    if usuario_objetivo is None:
        await update.message.reply_text("❌ No pude identificar al usuario objetivo.")
        return
    
    target_id = usuario_objetivo.id
    target_username = usuario_objetivo.username

    if target_id not in DOMS[actor_id]:
        await update.message.reply_text(f"❌ No puedes castigar a {target_username}. no tienes control sobre él/ella")
        return
    if chat_id not in USUARIOS_CASTIGADOS:
        USUARIOS_CASTIGADOS[chat_id] = set()

    USUARIOS_CASTIGADOS[chat_id].add(target_id)
    await update.message.reply_text(
        f"🔇 @{target_username} te has portado mal."
        "A partir de ahora tendrás que quedarte en el rincón, hasta que la persona que se encarga de ti, lo decida"
    )
async def filtro_castigo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    rincon_id = obtener_temas_por_comunidad(-1003397946543)["theme_rincon"]

    if chat_id not in USUARIOS_CASTIGADOS:
        return
    if user_id not in USUARIOS_CASTIGADOS[chat_id]:
        return
    topic = update.message.message_thread_id
    if topic != rincon_id:
        try:
            await update.message.delete()
        except:
            pass
async def perdonar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id
    actor_id = update.effective_user.id

    # 1. Verificar que se ejecuta en el grupo permitido
    if chat_id != -1003397946543:
        await update.message.reply_text("❌ Este comando no está habilitado en este grupo.")
        return

    # 2. Verificar permisos del actor
    if actor_id not in DOMS:
        await update.message.reply_text("❌ No tienes permiso para usar este comando.")
        return

    # 3. Identificar al usuario objetivo
    usuario_objetivo = await get_receptor(update, context, args_length=2)

    if usuario_objetivo is False:
        return

    if usuario_objetivo is None:
        await update.message.reply_text("❌ No pude identificar al usuario que deseas perdonar.")
        return

    target_id = usuario_objetivo.id
    target_username = usuario_objetivo.username or "SinUsername"

    # 4. Verificar si el admin puede perdonar a ese usuario
    if target_id not in DOMS[actor_id]:
        await update.message.reply_text(f"❌ No puedes perdonar a @{target_username}.")
        return

    # 5. Verificar si el usuario está castigado
    if (
        chat_id not in USUARIOS_CASTIGADOS
        or target_id not in USUARIOS_CASTIGADOS[chat_id]
    ):
        await update.message.reply_text(
            f"ℹ️ @{target_username} no está castigado."
        )
        return

    # 6. Remover castigo
    USUARIOS_CASTIGADOS[chat_id].remove(target_id)

    await update.message.reply_text(
        f"✅ @{target_username} ha sido perdonado. Ya puede hablar en todos los temas."
    )
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start),group = 0)
    app.add_handler(CommandHandler("castigar",castigar),group = 0)
    app.add_handler(CommandHandler("perdonar", perdonar),group = 0)
    
    # Handlers juegos
    app.add_handler(CommandHandler("apostar", apostar),group=1)
    app.add_handler(CommandHandler("aceptar", aceptar),group=1)
    app.add_handler(CommandHandler("cancelar", cancelar_apuesta),group=1)
    app.add_handler(CommandHandler("robar", robar),group=1)
    app.add_handler(CommandHandler("jugar", jugar),group=1)
    app.add_handler(MessageHandler(filters.Dice.DICE, detectar_dado),group=1)
    app.add_handler(CommandHandler("tienda", tienda))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^ver_comandos|abrir_tienda|ver_inventario|perfil$"))
    app.add_handler(CallbackQueryHandler(tienda_callback, pattern="^producto_"))

    # Handlers recompensas
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, manejar_imagenes),group=2)

    # Handlers de bienvenida
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, nuevo_usuario), group=3)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_de_presentaciones), group=3)

    # Handler de filtro castigo
    app.add_handler(MessageHandler(filters.ALL,filtro_castigo),group=4)

    # Handler general (para todos los chats)
    app.add_handler(CommandHandler("ver", ver),group=5)
    app.add_handler(CommandHandler("regalar", regalar),group=5)
    app.add_handler(CommandHandler("dar", dar),group=5)
    app.add_handler(CommandHandler("quitar", quitar),group=5)
    app.add_handler(CommandHandler("NumAzar", numero_azar),group=5)
    app.add_handler(CommandHandler("id", get_theme_id),group=5)
    app.add_handler(CommandHandler("saludar", saludar),group=5)
    
    app.add_handler(CallbackQueryHandler(menu_callback))
    
    print("🤖 Bot corriendo...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()