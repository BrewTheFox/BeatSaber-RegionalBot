import aiohttp
import json

async def songinfo(hash:str, dificulty:str) -> dict:
    session = aiohttp.ClientSession()
    async with session as ses:
        async with ses.get(f"https://api.beatsaver.com/maps/hash/{hash}") as request:
            datos = json.loads(await request.text())
    try:
        if not "error" in datos.keys():
            dificultad = dificulty.strip("_").split("_")
            for dificultades in datos["versions"][0]["diffs"]:
                if dificultades["difficulty"].lower() == dificultad[0].lower() and dificultades["characteristic"] in dificultad[1]:
                    return {"imagen":datos["versions"][0]["coverURL"],"notas":dificultades["notes"], "bombas":dificultades["bombs"], "dificultad":dificultades["difficulty"], "codigo":datos["id"], "nombre": datos["name"]}
            return {'imagen': 'https://cdn.scoresaber.com/avatars/steam.png', "notas":0, "bombas":0, "dificultad":"Desconocida", "codigo":"00000", "Nombre":"Cancion que no se encuentra en BeatSaver!", "error":True}
    except:
        return {'imagen': 'https://cdn.scoresaber.com/avatars/steam.png', "notas":0, "bombas":0, "dificultad":"Desconocida", "codigo":"00000", "Nombre":"Cancion que no se encuentra en BeatSaver / Conexion erronea!", "error":True}
    return datos

async def songexists(id:str) -> list:
    session = aiohttp.ClientSession()
    async with session as ses:
        async with ses.get(f"https://api.beatsaver.com/maps/id/{id}") as request:
            datos = json.loads(await request.text())
    try:
        if not "success" in datos.keys():
            return [True, datos["metadata"]["songName"], datos["versions"][-1]["coverURL"]]
        else:
            return [False]
    except:
        return [False]