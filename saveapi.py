import csv
import aiofiles
headers = ['id', 'discord', 'reto', 'puntos']

async def loadplayers() -> dict:
    global headers
    async with aiofiles.open("./save.csv", "r") as archivo:
        contenido = await archivo.readlines()
    jugadores = {}
    lector = csv.reader(contenido, delimiter=",")
    headers = next(lector)
    cantidadusuarios = 0
    for row in lector:
        cantidadusuarios += 1
        id = row[0]
        ds = row[1]
        reto = row[2]
        cantidad = row[3]
        if not id in jugadores:
            jugadores[id] = {"discord":ds, 'reto':{}}
        if reto != "NULL":
            print(reto)
            jugadores[id]['reto'][reto] = int(cantidad)
    print(str(cantidadusuarios) + " Usuarios cargados.")
    return jugadores

async def saveplayers(jugadores:dict):
    async with aiofiles.open("./save.csv", "w") as archivo:
        await archivo.write(",".join(headers) + "\n")
        for id_jugador, datos in jugadores.items():
            if datos['reto']:
                for tipo, cantidad in datos['reto'].items():
                    fila = f"{id_jugador},{datos['discord']},{tipo},{cantidad}\n"
                    await archivo.write(fila)
            else:
                fila = f"{id_jugador},{datos['discord']},NULL,NULL\n"
                await archivo.write(fila)
    print("Jugadores guardados.")