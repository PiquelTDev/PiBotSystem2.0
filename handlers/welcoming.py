import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from config import obtener_temas_por_comunidad

# Diccionario global para almacenar los usuarios en proceso de verificación
usuarios_en_verificacion = {}

# --- Handler principal: bienvenida ---
async def nuevo_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detecta nuevos miembros y los presenta en el tema de Presentaciones."""
    if not update.message or not update.message.new_chat_members:
        return

    group_id = update.effective_chat.id
    CHAT_IDS = obtener_temas_por_comunidad(group_id)
    
    if group_id not in usuarios_en_verificacion:
        usuarios_en_verificacion[group_id] = {}

    for miembro in update.message.new_chat_members:
        user_id = miembro.id
        username = miembro.username or miembro.first_name
        mention = f"@{username}" if miembro.username else username

        # Cancelar tareas anteriores si existían
        if user_id in usuarios_en_verificacion:
            usuarios_en_verificacion[user_id].cancel()

        # Crear la tarea de verificación de presentación
        task = asyncio.create_task(
            verificar_presentacion(
                context=context,
                group_id=group_id,
                user_id=user_id,
                username=username,
                CHAT_IDS=CHAT_IDS
            )
        )
        usuarios_en_verificacion[group_id][user_id] = task

        # Enviar mensaje directamente en el tema de presentaciones
        try:
            if group_id != -1003290179217:
                await context.bot.send_message(
                    chat_id = group_id,
                    message_thread_id=CHAT_IDS["theme_presentaciones"],  # ID del tema de presentaciones
                    text=(
                        f"👋 ¡Bienvenido {mention}!\n\n"
                        f"Por favor, preséntate aquí mismo en los próximos **15 minutos** 💬.\n"
                        f"Presentate con tu nombre, rol y que esperas encontrar en la comunidad.\n\n"
                        f"De lo contrario, un administrador **podrá expulsarte del grupo.**"
                    )
                )
            else:
                await context.bot.send_message(
                    chat_id = group_id,
                    text=(
                        f"👋 ¡Bienvenido {mention}!\n\n"
                        f"Por favor, preséntate aquí mismo en los próximos **15 minutos** 💬.\n"
                        f"Presentate con tu nombre, rol y que esperas encontrar en la comunidad.\n\n"
                        f"De lo contrario, un administrador **podrá expulsarte del grupo.**"
                    )
                ) 
        except Exception as e:
            if group_id != -1003290179217:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    message_thread_id=CHAT_IDS["theme_presentaciones"],
                    text=f"⚠️ Error al enviar mensaje de bienvenida para @{username}: {e}"
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"⚠️ Error al enviar mensaje de bienvenida para @{username}: {e}"
                )
            


# --- Verificación pasados los 15 minutos ---
async def verificar_presentacion(context: ContextTypes.DEFAULT_TYPE,group_id: int, user_id: int, username: str,CHAT_IDS: dict):
    """Espera 15 minutos y notifica al admin si el usuario no se presentó."""
    await asyncio.sleep(30*60)

    if group_id in usuarios_en_verificacion and user_id in usuarios_en_verificacion[group_id]:
        try:
            if group_id != -1003290179217:
                await context.bot.send_message(
                chat_id=group_id,
                message_thread_id=["theme_presentaciones"],
                text=f"@Admin ⚠️ El usuario @{username} no se presentó en los 30 minutos posteriores a su ingreso."
            )
            else:
                await context.bot.send_message(
                chat_id=group_id,
                text=f"@Admin ⚠️ El usuario @{username} no se presentó en los 30 minutos posteriores a su ingreso."
            )
            print(f"El usuario {username} no se ha presentado, se envía notificación")
        except Exception as e:
            print(f"Error al notificar sobre @{username}: {e}")
        del usuarios_en_verificacion[group_id][user_id]

# --- Monitoreo de mensajes ---
async def mensaje_de_presentaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detecta si el usuario ya se presentó en el tema correcto."""
    if not update.message or not update.effective_user:
        return

    group_id = update.effective_chat.id
    user_id = update.effective_user.id
    thread_id = getattr(update.message, "message_thread_id", None)

    if group_id not in usuarios_en_verificacion:
        return
    
    CHAT_IDS = obtener_temas_por_comunidad(group_id)

    # Si el mensaje está en el tema de presentaciones
    if thread_id == CHAT_IDS.get("theme_presentaciones"):
        if user_id in usuarios_en_verificacion:
            del usuarios_en_verificacion[user_id]
            print(f"✅ {update.effective_user.username} se presentó correctamente.")
        
