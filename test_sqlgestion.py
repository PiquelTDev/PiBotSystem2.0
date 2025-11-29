# test_database.py
import sqlite3
import pytest

# Importa tus funciones desde database.py
from sqlgestion import connect,insert_user,insert_item,insert_user_item,delete_user,delete_item,update_item,update_perfil,update_user,get_campo_usuario,get_campo_item,get_items

# -------------------------
# FIXTURE DE BASE DE DATOS
# -------------------------

# -------------------------
# TEST: crear usuario
# -------------------------
def test_insertar():
    assert insert_user(1005894144,100,"Magenta_20","Miguel") == True
    assert insert_user(1853282015,150,"","Nombre generico") == True
    assert insert_user(None,50,"Ara","Nombre generico 2") == False
    assert insert_user(1005894145,"Kiusama") == False
    assert insert_user(1005894144,"Magenta_20","Miguel") == False
    assert insert_item("item_1",1000,"ruta/img/") == True
    assert insert_item("item_2",1000,"ruta/img/") == True
    assert insert_item("item_3",1000,"ruta/img/") == True

def test_delete():
    db = connect()
    cursor = db.cursor()
    assert delete_user(1005894144) == True
    assert delete_user(1853282015) == True
    assert delete_user(1005894145) == False
    
    cursor.execute("SELECT id_user FROM usuarios_tb WHERE id_user = 1005894144")
    assert cursor.fetchone() == None
    cursor.execute("SELECT id_user FROM usuarios_tb WHERE id_user = 1853282015")
    assert cursor.fetchone() == None
    cursor.execute("SELECT id_user FROM perfiles_tb WHERE id_user = 1005894144")
    assert cursor.fetchone() == None
    cursor.execute("SELECT id_user FROM perfiles_tb WHERE id_user = 1853282015")
    assert cursor.fetchone() == None

    db.commit()
    db.close()

def test_select():
    assert get_campo_usuario(1005894144,"username") == "Magenta_20"
    assert get_campo_usuario(1005894144,"nombre") == "Miguel"
    assert get_campo_usuario(1005894144,"rol") == None
    assert get_campo_usuario(1005894144,"orientacion_sexual") == None
    assert get_campo_usuario(1005894144,"genero") == None
    assert get_campo_usuario(1005894144,"ubicacion") == None
    assert get_campo_usuario(1005894144,"edad") == None
    assert get_campo_usuario(1005894144,"saldo") == 100
    assert get_campo_usuario(1005894144,"variable") == False
    assert get_campo_usuario(1005894145,"username") == None

    assert get_campo_item(21,"nombre") == "item_3"
    assert get_campo_item(19,"precio") == 1000
    assert get_campo_item(20,"imagen") == "ruta/img/"
    assert get_campo_item(24,"precio") == None

def test_case1():
    #creción de usuarios
    assert insert_user(1005894144,10,"Magenta_20","Miguel") == True
    assert insert_user(1562158624,10,"Kiusama","Kiu") == True

    #creacion de items:
    assert insert_item("galleta",10,"ruta/img/") == True
    assert insert_item("paleta",20,"ruta/img/") == True
    assert insert_item("barilla",50,"ruta/img/") == True
    assert insert_item("esposas",75,"ruta/img/") == True

    insert_user_item(1005894144,1,1)
    insert_user_item(1005894144,3,1)
    insert_user_item(1005894144,3,1)

    insert_user_item(1562158624,2,1)
    insert_user_item(1562158624,3,2)
    insert_user_item(1562158624,3,1)

def test_case2():
    assert delete_user(1005894144) == True

def test_case3():
    assert delete_item(2) == True

def test_update_user():
    insert_user(1005894144,10,"Magenta_20","Miguel")
    insert_user(1562158624,10,"Kiusama","Kiu")

    update_perfil(1005894144,username="Magenta_21",rol="Sumiso",edad=21,genero="Hombre")
    assert get_campo_usuario(1005894144,"username") == "Magenta_21"

    insert_item("Item_1",100,"ruta/img/")
    update_item(1,nombre="galleta",precio=150)
    assert get_campo_item(1,"nombre") == "galleta"

def test_get_items():
    items = get_items(1005894144)

    print("======")
    for item in items:
        print(item["id_item"])
    print("======")
    assert True == True
    