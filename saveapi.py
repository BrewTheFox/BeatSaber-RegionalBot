import csv
headers = ['id', 'discord', 'reto', 'puntos']

def loadplayers() -> dict:
    global headers
    with open("./save.csv", "r") as archivo:
        jugadores = {}
        lector = csv.reader(archivo, delimiter=",")
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
                jugadores[id]['reto'][reto] = int(cantidad)
        print(str(cantidadusuarios) + " Usuarios cargados.")
        return jugadores

def saveplayers(jugadores:dict):
    with open("./save.csv", "w") as archivo:
        escritor = csv.writer(archivo, delimiter=",")
        escritor.writerow(headers)
        for id_jugador, datos in jugadores.items():
            if datos['reto']:
                for tipo, cantidad in datos['reto'].items():
                    fila = [id_jugador, datos['discord'], tipo, cantidad]
                    escritor.writerow(fila)
            else:
                fila = [id_jugador, datos['discord'], 'NULL', 'NULL']
                escritor.writerow(fila)
    print("Jugadores guardados.")