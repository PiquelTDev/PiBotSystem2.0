import os

BOT_TOKEN = "8254671233:AAEJaciszQQ3Ub_ccprFb6HbH0yb101RY0s" #os.getenv("BOT_TOKEN")
# IDs de los chats/grupos

COMUNIDADES = [
    {
        "id_comunidad":-1003397946543, #Ara
        "temas":{
            "theme_presentaciones": 7,
            "theme_anuncios": 396,
            "theme_questions": 439,
            "theme_escuela": 3,
            "theme_juegosYcasino":362, #362
            "theme_cgl":8,
            "theme_NSFW":5,
            "theme_Exhibicionismo":9,
            "theme_busquedas":1606,
            "theme_zona_de_descanso":2,
            "theme_multimedia":4,
            "theme_rincon": 6
        }
    },
    {
        "id_comunidad":-1003290179217, #Kiusama
        "temas":{
            "theme_anuncios": 526,
            "theme_questions": 902,
            "theme_escuela": 438,
            "theme_juegosYcasino":528, #528
            "theme_relatos":683,
            "theme_NSFW":2,
            "theme_Exhibicionismo":437,
            "theme_busquedas":695,
            "theme_libreria":462,
            "theme_multimedia":688
        }
    },
    {
        "id_comunidad":-1002983018006, #Rub
        "temas":{
            "theme_Anuncios": 207,
            "theme_questions": 7,
            "theme_escuela": 438,
            "theme_juegosYcasino":16785, #528
            "theme_NSFW":5,
            "theme_Exhibicionismo":4,
            "theme_libreria": 3,
            "theme_multimedia":15,
            "theme_platica": 28175,
            "theme_test":43,
            "theme_reglas":8,
            "theme_escuela":6,
            "theme_presentaciones":2
        }
    }
]

DOMS = {
    1370162159: [5661536115],
    1174798556: [7064982957,7819911906,1128700552]
}
def obtener_temas_por_comunidad(community_id: int):
    for comunidad in COMUNIDADES:
        if comunidad["id_comunidad"] == community_id:
            return comunidad["temas"]
    return None  # Si no se encuentra, retorna None

