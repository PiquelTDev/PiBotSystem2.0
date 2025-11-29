def eliminar_usuario_especifico(id_user):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor.execute("DELETE FROM usuarios_tb WHERE id_user = ?", (id_user,))
        conn.commit()
        print(f"Usuario {id_user} eliminado correctamente.")
    except Exception as e:
        print(f"Error eliminando usuario {id_user}: {e}")
    finally:
        conn.close()


# ---- Ejecutar eliminación ----
if __name__ == "__main__":
    eliminar_usuario_especifico(1128700552)