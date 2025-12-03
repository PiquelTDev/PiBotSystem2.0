import random
from telegram import Update
from telegram.ext import ContextTypes

from sqlgestion import get_campo_usuario,normalizar_nombre,update_perfil,insert_user,get_id_user,quitar_puntos,dar_puntos

#region FUNCIONES AUXILIARES
async def verificar_admin(user_id: int, update: Update) -> bool:
    chat = update.effective_chat
    try:
        # Obtiene los administradores del chat actual
        administradores = await chat.get_administrators()

        # Recorre los administradores para verificar si el ID coincide
        for admin in administradores:
            if admin.user.id == user_id:
                return True
        return False
    except Exception as e:
        print(f"Error verificando admin: {e}")
        return False
    
async def get_receptor(update: Update, context: ContextTypes.DEFAULT_TYPE,args_length=-1):
    if len(context.args) == 0:
        return None
    
    if len(context.args) >= args_length:
        if not context.args[args_length-1].startswith("@"):
            await update.message.reply_text("⚠️ No es posible identificar al usuario sin un arroba, puede usar el comando respondiendo a uno de los mensajes del usuario al que desea enviarle los PiPesos")
            return False
        
        mention = context.args[args_length-1].lstrip("@")
        user_id = get_id_user(mention)
        if not user_id is None:
            receptor = type("obj", (object,), {"id": int(user_id), "username": mention})
        else:
            receptor = None
    elif update.message.reply_to_message:
        try:
            receptor = update.message.reply_to_message.from_user
            if get_campo_usuario(receptor.id,"id_user") is None:
                insert_user(receptor.id,0,receptor.username,normalizar_nombre(receptor.first_name,receptor.last_name))
                print(f"[LOG - GENERAL] Se ha ingrsado un nuevo usuario {receptor.id}-{receptor.username or normalizar_nombre(receptor.first_name,receptor.last_name)}")
        except Exception as e:
            print(f"[ERROR] No se ha podido identificar al usuario: {e}")
            receptor = None
    else:
        receptor = None
    return receptor
#endregion




#region COMANDOS USO GENERAL
async def ver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("================================0================================")
    user = update.effective_user
    
    tmp_nombre = normalizar_nombre(user.first_name,user.last_name)
    tmp_username = user.username
    sql_username = get_campo_usuario(user.id,"username")
    sql_nombre = get_campo_usuario(user.id,"nombre")

    if get_campo_usuario(user.id,"id_user") is None:
        insert_user(user.id,0,tmp_username,tmp_nombre)
        print(f"[LOG - VER] Nuevo usuario registrado: {user.id} - {tmp_username or tmp_nombre}")
        sql_username = tmp_username
        sql_nombre = tmp_nombre

    if sql_username != tmp_username or sql_nombre != tmp_nombre:
        print(f"[LOG - VER] Nuevo username detectado, actualizando: {sql_username} a {tmp_username}")
        print(f"[LOG - VER] Nuevo nombre detectado, actualizando: {sql_nombre} a {tmp_nombre}")
        update_perfil(user.id,username=tmp_username,nombre=tmp_nombre)
        sql_username = tmp_username
        sql_nombre = tmp_nombre

    saldo = get_campo_usuario(user.id,"saldo")
    
    if saldo == False or saldo == None:
        print(f"[ERROR - VER] No se ha podido encontrar el saldo del usuario: {user.id}-{sql_username or sql_nombre}: saldo: {saldo}")
        saldo = 0

    await update.message.reply_text(
        f"💰 {sql_username}, tienes {saldo} PiPesos."
    )

    print(f"[GENERAL - VER] El usuario {user.id}- {sql_username or sql_nombre} ha consultado su saldo")
    print("================================1================================\n")
async def dar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("================================0================================")
    sender = update.effective_user

    if not context.args:
        await update.message.reply_text("Uso: /dar <cantidad> [@usuario] o respondiendo a un mensaje.")
        return

    try:
        cantidad = int(context.args[0])
    except ValueError:
        await update.message.reply_text("⚠️ La cantidad debe ser un número.")
        return

    if cantidad <= 0:
        await update.message.reply_text("⚠️ La cantidad debe ser mayor a 0.")
        return
    
    receptor = await get_receptor(update,context,2)

    if receptor is None or receptor is False:
        await update.message.reply_text("⚠️ No se encontró al usuario receptor o no ha sido ingresado al sistema aún, si está usando @ evitelos y use el comando respondiendo un mensaje")
        return

#    if sender.id == 5661536115 and receptor.id != 1370162159:
#        await update.message.reply_text("No no Ara, debes tener permiso de tu dueño @Nicolas_Dom si quieres usar tus pipesos, te has portado mal")
#        return
    
    # Verificar saldo del emisor
    sender_id = sender.id
    sql_sender_username = get_campo_usuario(sender_id,"username")
    tmp_sender_username = sender.username
    sql_sender_nombre = get_campo_usuario(sender_id,"nombre")
    tmp_sender_nombre = normalizar_nombre(sender.first_name,sender.last_name)

    if get_campo_usuario(sender.id,"id_user") is None:
        insert_user(sender_id,0,tmp_sender_username,tmp_sender_nombre)
        print(f"[LOG - DAR] Se ha ingresado un nuevo usuario {sender_id}-{tmp_sender_username} ")
        sql_sender_nombre = tmp_sender_nombre
        sql_sender_username = tmp_sender_username
    
    if tmp_sender_nombre != sql_sender_nombre or tmp_sender_username != sql_sender_username:
        update_perfil(sender_id,username=tmp_sender_username,nombre=tmp_sender_nombre)
        print(f"[LOG - DAR] Se ha actualizado el usuario {sender_id}-{sql_sender_username or sql_sender_nombre}")
        sql_sender_nombre = tmp_sender_nombre
        sql_sender_username = tmp_sender_username

    sender_saldo = get_campo_usuario(sender_id,"saldo")
    
    receptor_id = receptor.id
    receptor_username = receptor.username
    
    if sender_saldo < cantidad:
        await update.message.reply_text(f"💸 Saldo insuficiente. Tienes {sender_saldo} PiPesos.")
        return
    print(f"[LOG - DAR] Usuario que da: {sender_id}-{sql_sender_username}")
    print(f"[LOG - DAR] Usuario que recibe: {receptor_id}-{receptor_username}")

    quitar_puntos(sender_id,cantidad)
    dar_puntos(receptor.id,cantidad)

    print(f"Se le  ha dado: {cantidad} a {receptor_username} correctamente")
    await update.message.reply_text(
        f"🤝 {sql_sender_username or sql_sender_nombre} dio {cantidad} PiPesos a "
        f"{receptor_username}"
    ) 
    print("================================1================================\n")
async def numero_azar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("================================0================================")
    
    if len(context.args) < 2:
        return await update.message.reply_text(
            "Uso: /numeroazar N1 N2\nEjemplo: /numeroazar 5 15",
            reply_to_message_id=update.message.message_id
        )

    try:
        n1 = int(context.args[0])
        n2 = int(context.args[1])
    except ValueError:
        return await update.message.reply_text(
            "❌ Los parámetros deben ser números enteros.",
            reply_to_message_id=update.message.message_id
        )

    if n1 > n2:
        n1, n2 = n2, n1  # si los ponen al revés, los acomodamos

    resultado = random.randint(n1, n2)

    await update.message.reply_text(
        f"🎲 Número al azar entre {n1} y {n2}: **{resultado}**",
        parse_mode="Markdown",
        reply_to_message_id=update.message.message_id
    )
    print("================================0================================")
#endregion




#region COMANDOS ADMINS
# TODO arreglar la funcion de quitar - temporalmente eliminada por mal uso
async def quitar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    """Comando /quitar: solo admins, quita puntos a un usuario."""
    print("================================0================================")
    sender = update.effective_user
    
    if not await verificar_admin(sender.id, update):
        await update.message.reply_text("⚠️ Solo los administradores pueden usar este comando.")
        return

    # Verificar que haya al menos un argumento (cantidad)
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /quitar <cantidad>")
        return
    
    # Intentar convertir la cantidad
    try:
        cantidad = int(context.args[0])
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("La cantidad debe ser un número mayor que 0.")
        return

    receptor = await get_receptor(update,context,2)
    if receptor is None or receptor is False:
        await update.message.reply_text("No es posible identificar al usuario")
        return

#    if sender.id == 5661536115 and receptor.id != 1370162159:
#        await update.message.reply_text("No no Ara, debes tener permiso de tu dueño @Nicolas_Dom si quieres usar tus pipesos, te has portado mal")
#        return

    receptor_id = receptor.id
    receptor_username = receptor.username
    # Quitar puntos

    quitar_puntos(receptor_id, cantidad)
    print(f"[LOG-QUITAR] Se le han quitado {cantidad} a {receptor_username}")
    await update.message.reply_text(
        f"✅ Se han quitado {cantidad} PiPesos a @{receptor_username}."
    )
    print("================================0================================")
async def regalar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("================================0================================")
    sender = update.effective_user
    
    # 🔐 Verificar admin
    if not await verificar_admin(sender.id, update):
        await update.message.reply_text("⚠️ Solo los administradores pueden usar este comando.")
        return

    if not context.args:
        await update.message.reply_text("Uso: /regalar <cantidad> [@usuario] o respondiendo a un mensaje.")
        return

    try:
        cantidad = int(context.args[0])
    except ValueError:
        await update.message.reply_text("⚠️ La cantidad debe ser un número.")
        return

    if cantidad <= 0:
        await update.message.reply_text("⚠️ La cantidad debe ser mayor a 0.")
        return

    if cantidad > 200:
        await update.message.reply_text("⚠️ No hay necesidad de regalarse tanto, limitar a 200.")
        return
    
    receptor = await get_receptor(update,context,2)

    if receptor is None or receptor is False:
        await update.message.reply_text("⚠️ No fue posible identificar al usuario")
        return
    
#    if sender.id == 5661536115 and receptor.id != 1370162159:
#        await update.message.reply_text("No no Ara, debes tener permiso de tu dueño @Nicolas_Dom si quieres usar tus pipesos, te has portado mal")
#        return
    receptor_id = receptor.id
    receptor_username = receptor.username
    
    dar_puntos(receptor_id,cantidad)

    print(f"[LOG] Se le han regalado {cantidad} a {receptor_username}")
    await update.message.reply_text(
        f"🎁 {sender.username} regaló {cantidad} PiPesos a "
        f"{receptor_username}"
    )
    print("================================0================================")
#endregion