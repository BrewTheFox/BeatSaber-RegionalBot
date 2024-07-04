import saveapi

jugadores = saveapi.loadplayers()

def fetchjugadores() -> dict:
    return jugadores

def setjugadores(newjugadores:dict) -> dict:
    global jugadores
    jugadores = newjugadores
    saveapi.guardarjugadores(jugadores)
    return jugadores
