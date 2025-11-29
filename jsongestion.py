import json
import os
import re
import unicodedata
from config import RUTA_USUARIOS # type: ignore

def cargar_usuarios():
    if not os.path.exists(RUTA_USUARIOS):
        print("[ERROR] Ruta de usuario no encontrada")
        return {}
    try:
        with open(RUTA_USUARIOS,"r",encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError,FileNotFoundError) as e:
        print(f"[ERROR] {e}")
        return {}
    
    if isinstance(data,dict) and "usuarios" in data and isinstance(data["usuarios"],dict):
        return data["usuarios"]
    
    return {}

def guardar_usuarios(usuarios: dict):
    payload = {"usuarios":usuarios}
    tmp = RUTA_USUARIOS + ".tmp"
    with open(tmp, "w",encoding="utf-8" ) as f:
        json.dump(payload,f,indent=4,ensure_ascii=False)
    os.replace(tmp,RUTA_USUARIOS)

def get_value(id_integer:int,parameter:str):
    usuarios = cargar_usuarios()
    id_str = str(id_integer)
    if id_str not in usuarios:
        return False
    return usuarios[id_str].get(parameter)

def set_value(id_integer:int,parameter:str,value):
    usuarios = cargar_usuarios()
    id_str = str(id_integer)
    usuarios[id_str][parameter] = value
    guardar_usuarios(usuarios)
    return True

def obtener_id(username: str):
    """Devuelve el id cuyo nombre de usuario coincida con el username entregado o con la versón normalizada del mismo, si el usuario no tiene username y en su lugar tiene firs_name y last_name, se debe de normalizar el texto antes de entregarlo como parametro"""
    usuarios = cargar_usuarios()
    normalizedUsername = normalizar_nombre(username)
    
    for user_id, data in usuarios.items():
        if data.get("username") == username:
            return int(user_id)
        if data.get("username") == normalizedUsername:
            return int(user_id)
    return None

def existe_usuario(user_id: int):
    """Devuelve True o False si el usuario ya existe, utiliza el id para buscar en el archivo json"""
    usuarios = cargar_usuarios()
    id_str = str(user_id)
    if id_str not in usuarios:
        return False
    return True

def actualizar_usuario(id_usuario: int, new_username: str, new_saldo: int=-1):
    if not existe_usuario(id_usuario):
        print(f"[ERROR - ACTUALIZAR] No se puede actualizar, el usuario {id_usuario} - {new_username} no existe")
        return False
    
    set_value(id_usuario,"username",new_username)
    if new_saldo != -1:
        set_value(id_usuario,"saldo",new_saldo)

    print(f"[LOG - ACTUALIZAR] Usuario {new_username} con id: {id_usuario} ha sido actualiado correctamente")
    return True

def agregar_usuario(id_usuario: int,cantidad: int, username: str):
    
    if existe_usuario(id_usuario):
        print(f"[ERROR - AGREGAR] El usuario {id_usuario} - {username} ya existe en el json, no se puede crear un nuevo usuario")
        return False

    usuarios = cargar_usuarios()
    id_str = str(id_usuario)
    
    usuarios[id_str] = {
        "username": username,
        "saldo": cantidad
    }

    guardar_usuarios(usuarios)
    print(f"[LOG - AGREGAR] Nuevo usurio creado con id: {id_str} y usuario: {username}")
    return True

def dar_puntos(user_id: int, cantidad: int):

    if cantidad < 0:
        function = "QUITAR"
    else:
        function = "DAR"
    
    if not existe_usuario(user_id):
        print(f"[ERROR - {function}] No se le pueden {function.lower()} puntos al usuario, no existe")
        return False
    
    if set_value(user_id,"saldo",get_value(user_id,"saldo")+cantidad):
        print(f"[LOG - {function}] {function.lower()} {cantidad} puntos a {user_id}-{get_value(user_id,"username")} ha sido usado correctamente")
        return True
    
    print(f"[ERROR - {function}] no se le ha podido {function.lower()} {cantidad} de puntos a {user_id}-{get_value(user_id,"username")}")
    return False

def quitar_puntos(user_id:int,cantidad):
    return dar_puntos(user_id,-cantidad)

def normalizar_nombre(first_name:str,last_name:str = "") -> str:
    nombre_completo = f"{to_plain_text(first_name) or ''} {to_plain_text(last_name) or ''}".strip()
    nombre_completo = re.sub(r'[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü ]+', '', nombre_completo)
    nombre_completo = unicodedata.normalize("NFKD",nombre_completo)
    nombre_completo = ''.join(
        c for c in nombre_completo
        if not unicodedata.combining(c)
    )
    nombre_completo = re.sub(r'\s+', ' ', nombre_completo).strip().lower()
    return nombre_completo

def to_plain_text(s:str,keep_space:bool = False) -> str:
    out_chars = []
    try:
        for ch in s:
            # 1) Normaliza compuestos (NFKD separa diacríticos)
            ch_nfd = unicodedata.normalize("NFKD", ch)

            # Recorremos la secuencia normalizada (por si hay letras + marcas)
            for ch2 in ch_nfd:
                cat = unicodedata.category(ch2)

                # Ignorar marcas combinantes (diacríticos) y control/format invisibles
                if cat.startswith("M"):  # Mark (combining)
                    continue
                if cat in ("Cc", "Cf"):  # Control / Format
                    continue

                # Si es ASCII alfanumérico lo aceptamos tal cual
                if '0' <= ch2 <= '9' or 'A' <= ch2 <= 'Z' or 'a' <= ch2 <= 'z':
                    out_chars.append(ch2)
                    continue

                # Tratamiento por nombre Unicode: muchas letras "fancy" incluyen
                # "LATIN ... LETTER <X>" en su nombre (p. ej. MATHEMATICAL BOLD CAPITAL A,
                # CIRCLED LATIN SMALL LETTER A, etc.). Intentamos extraer la letra base.
                try:
                    name = unicodedata.name(ch2)
                except ValueError:
                    name = ""

                if "LATIN" in name and "LETTER" in name:
                    # Buscamos la última token después de 'LETTER ' (p.ej. 'LATIN CAPITAL LETTER A' -> 'A')
                    m = re.search(r"LETTER\s+([A-Z]+[A-Z0-9]*)$", name)
                    if m:
                        token = m.group(1)
                        # token puede ser 'AE' o similar; tomamos cada letra por separado si corresponde
                        # pero normalmente es una sola letra A..Z
                        for c in token:
                            if 'A' <= c <= 'Z':
                                out_chars.append(c)
                        continue

                # Algunos símbolos son separadores (espacios invisibles) -> tratarlos como espacio
                if cat.startswith("Z"):  # Separator (space, line sep, paragraph sep)
                    out_chars.append(" ")
                    continue

                # Otros caracteres decorativos (p. ej. dingbats, ornamentos) los ignoramos.
                # Si quisieras conservar dígitos de otros scripts, podrías mapearlos aquí.
                # Por defecto: ignorar.
                # continue -> implica no añadir nada

        # unir, normalizar espacios, limpiar no-alphanum según preferencia
        text = "".join(out_chars)

        if keep_space:
            # Normalizar múltiples espacios a uno y recortar
            text = re.sub(r"\s+", " ", text).strip()
            # Ahora eliminar cualquier carácter que no sea ASCII alfanumérico o espacio
            text = re.sub(r"[^0-9A-Za-z ]+", "", text)
        else:
            # Eliminar todo excepto ASCII alfanumérico
            text = re.sub(r"[^0-9A-Za-z]+", "", text)

        return text.lower()
    except TypeError:
        return ""