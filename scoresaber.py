import requests
import discord
import json
import re
import websockets
import playerhandler
import os

jugadores = playerhandler.fetchjugadores()

def getplayerinfo(did:int) -> list:
    jugadores = playerhandler.fetchjugadores()
    for jugador in jugadores.keys():
        if str(jugadores[jugador]["discord"]) == str(did):
            datos = json.loads(requests.get(f"https://scoresaber.com/api/player/{jugador}/full").text)
            embed = discord.Embed(title=f"¡Perfil de {datos['name']}!", color=discord.Color.green())
            embed.set_thumbnail(url=datos['profilePicture'])
            embed.add_field(name="🌎", value=f"#{datos['rank']}", inline=True)
            code_points = [127397 + ord(char) for char in datos['country'].upper()]
            embed.add_field(name=''.join(chr(code) for code in code_points), value=f'#{datos["countryRank"]}', inline=True)
            embed.add_field(name="PP:", value=str(datos["pp"]), inline=False)
            embed.add_field(name="Puntaje total:", value=str('{:20,.0f}'.format(datos["scoreStats"]["totalScore"])), inline=False)
            embed.add_field(name="Juegos totales:", value=str(datos["scoreStats"]["totalPlayCount"]), inline=False)
            embed.add_field(name="Fecha de registro:", value=str(datos["firstSeen"]), inline=False)
            embed.set_footer(text="Bot por @brewthefox :D")
            return embed, False
    embed = discord.Embed(title="¡No hay una cuenta de scoresaber vinculada a este usuario!", color=discord.Color.red())
    embed.add_field(name="**Si la consulta es para ti usa /vincular, si es para otro usuario pidele que vincule su cuenta.**", value=" ")
    return embed, True

async def recibir(client):
    print(client.guilds)
    while True:
        try:
            async with websockets.connect("wss://scoresaber.com/ws") as socket:
                while True:
                    datos = await socket.recv()
                    if datos and "{" in datos:
                        await playerhandler.checklocalplayerdata(client)
                        datos = json.loads(datos)
                        datos["Scoresaber"] = True
                        jugadores = playerhandler.fetchjugadores()
                        if datos["commandData"]["score"]['leaderboardPlayerInfo']['country'] == os.getenv("pais") or str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]) in jugadores.keys():
                            print("Se encontro un jugador.")
                            gameid = datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]
                            playerhandler.updatelocalplayerdata(gameid,datos)
                        else:
                            await playerhandler.playsplusone(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"], "scoresaber", client)
        except Exception as e: 
            try:
                print("Ocurrio un error, reestableciendo")
                print(e)
            except:
                print("No existen datos para mostrar")
