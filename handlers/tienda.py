import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from sqlgestion import get_campo_usuario

async def tienda (update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat = update.effective_chat

    if chat.type != "private":
        deep_link = f"https://t.me/PiBotBotBotBotBot?start=menu"

        keyboard = [
            [InlineKeyboardButton("✨ Abrir menú principal", url=deep_link)]
        ]

        await update.message.reply_text(
            "🛍️ La tienda solo está disponible en el chat privado.\n"
            "Haz clic en el botón para abrir el menú principal:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if get_campo_usuario(user_id,"id_user") is None:
        await update.message.reply_text(
            "⚠️ No estás registrado.\nUsa /ver en el chat general de la comunidad para registrarte primero."
        )
        return
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RUTA_CATALOGO = os.path.join(BASE_DIR, "img_itemS", "catalogo.jpg")

    await update.message.reply_photo(
        photo=RUTA_CATALOGO,
        caption="🛍️ **Catálogo de Productos**\nSelecciona el número del producto que deseas ver.",
        parse_mode="Markdown"
    )
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data="producto_1"),
            InlineKeyboardButton("2️⃣", callback_data="producto_2"),
            InlineKeyboardButton("3️⃣", callback_data="producto_3"),
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data="producto_4"),
            InlineKeyboardButton("5️⃣", callback_data="producto_5"),
            InlineKeyboardButton("6️⃣", callback_data="producto_6"),
        ] 
    ]
    await update.message.reply_text(
        "👇 Selecciona un producto:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def tienda_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Aquí puedes conectar con tu BD / precios / stock
    productos = {
        "producto_1": "Producto 1 — 💲50 monedas",
        "producto_2": "Producto 2 — 💲80 monedas",
        "producto_3": "Producto 3 — 💲120 monedas",
        "producto_4": "Producto 4 — 💲200 monedas",
        "producto_5": "Producto 5 — 💲450 monedas",
        "producto_6": "Producto 6 — 💲1000 monedas",
    }

    if data in productos:
        await query.message.reply_text(f"🛒 {productos[data]}")