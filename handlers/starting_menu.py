# starting_menu.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlgestion import insert_user,normalizar_nombre,get_campo_usuario

# =========  COMANDO /START  ========= #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if get_campo_usuario(user.id,"id_user") is None:
        context.bot.send_message("🎉 Veo que eres nuevo, no te tengo en mi sistema, si deseas ingresar a la tienda o a tu perfil, primero coloca el comando /ver en la comunidad ;D (No olvides leer las reglas)")
        return
    # Guardar usuario en la BD

    # Solo mostrar menú si está en privado
    if update.message.chat.type != "private":
        await update.message.reply_text("Envíame /start por privado para ver el menú.")
        return

    keyboard = [
        [InlineKeyboardButton("📜 Ver comandos", callback_data="ver_comandos")],
        [InlineKeyboardButton("🛍️ Abrir tienda", callback_data="abrir_tienda")],
        [InlineKeyboardButton("📦 Ver inventario", callback_data="ver_inventario")],
        [InlineKeyboardButton("👤 Perfil", callback_data="perfil")]
    ]

    await update.message.reply_text(
        "✨ **Menú principal**\nSelecciona una opción:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========  CALLBACK DEL MENÚ  ========= #
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == "ver_comandos":
        await query.message.reply_text(
            "📜 *Comandos disponibles:*\n"
            "/tienda \n"
            "/perfil\n"
            "/ver\n"
            "/dar\n"
            "/jugar\n"
            "/robar\n"
            "/apostar\n"
            "/aceptar\n",
            parse_mode="Markdown"
        )

    elif data == "abrir_tienda":
        await query.message.reply_text("🛍️ Abriendo tienda…")

    elif data == "ver_inventario":
        await query.message.reply_text("📦 Tu inventario está vacío (por ahora).")

    elif data == "perfil":
        await query.message.reply_text(
            f"👤 *Perfil de {user.first_name}*\n"
            f"ID: `{user.id}`",
            parse_mode="Markdown"
        )
