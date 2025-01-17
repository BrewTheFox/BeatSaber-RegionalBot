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
            return {'error': 'Not Found'}
    except:
        return {'error': 'Internal'}
    return datos
