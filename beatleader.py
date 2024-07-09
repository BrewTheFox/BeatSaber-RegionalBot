import websockets
import playerhandler
import json
import os
async def recibir(client):
    while True:
        try:
            async with websockets.connect("wss://sockets.api.beatleader.xyz/scores") as socket:
                while True:
                    await playerhandler.checklocalplayerdata(client)
                    datos = await socket.recv()
                    if datos and "{" in datos:
                        jugadores = playerhandler.fetchjugadores()
                        await playerhandler.checklocalplayerdata(client)
                        datos = json.loads(datos)
                        datos["Beatleader"] = True
                        await playerhandler.playsplusone(datos["playerId"], "Beatleader", client)
                        if datos['country'] == os.getenv("pais") or str(datos["playerId"]) in jugadores.keys():
                            print(datos["player"]["name"])
                            print("Se registro un juego.")
                            playerhandler.updatelocalplayerdata(int(datos["playerId"]), datos)
        except Exception as e:
            print(e)