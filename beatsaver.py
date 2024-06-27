import requests
import json

def songinfo(hash:str, dificulty:str) -> dict:
    datos = json.loads(requests.get(f"https://api.beatsaver.com/maps/hash/{hash}").text)
    try:
        if not "error" in datos.keys():
            dificultad = dificulty.strip("_").split("_")
            for dificultades in datos["versions"][0]["diffs"]:
                if dificultades["difficulty"].lower() == dificultad[0].lower() and dificultades["characteristic"] in dificultad[1]:
                    return {"notas":dificultades["notes"], "bombas":dificultades["bombs"], "dificultad":dificultades["difficulty"], "codigo":datos["id"]}
            return {'error': 'Not Found'}
    except:
        return {'error': 'Internal'}
    return datos
