import websockets
import playerhandler
import json
import os
import aiohttp
import discord
import asyncio

jugadores = playerhandler.fetchjugadores()

async def getplayerinfo(did:int) -> list:
    session = aiohttp.ClientSession()
    jugadores = playerhandler.fetchjugadores()
    for jugador in jugadores.keys():
        if str(jugadores[jugador]["discord"]) == str(did):
            async with session as ses:
                async with ses.get(f"https://api.beatleader.xyz/player/{jugador}?stats=true&keepOriginalId=false") as request:
                    datos = json.loads(await request.text())
                    await session.close()
            embed = discord.Embed(title=f"¡Perfil de {datos['name']}!", color=discord.Color.purple())
            embed.set_thumbnail(url=datos['avatar'])
            embed.add_field(name="🌎", value=f"#{datos['rank']}", inline=True)
            code_points = [127397 + ord(char) for char in datos['country'].upper()]
            embed.add_field(name=''.join(chr(code) for code in code_points), value=f'#{datos["countryRank"]}', inline=True)
            embed.add_field(name="PP:", value=str(datos["pp"]), inline=False)
            embed.add_field(name="Puntaje total:", value=str('{:20,.0f}'.format(datos["scoreStats"]["totalScore"])), inline=False)
            embed.add_field(name="Juegos totales:", value=str(datos["scoreStats"]["totalPlayCount"]), inline=False)
            embed.set_footer(text="Bot por @brewthefox :D")
            return embed, False
    embed = discord.Embed(title="¡No hay una cuenta de scoresaber vinculada a este usuario!", color=discord.Color.red())
    embed.add_field(name="**Si la consulta es para ti usa /vincular, si es para otro usuario pidele que vincule su cuenta.**", value=" ")
    return embed, True


async def recieve(client:discord.Client):
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
                        asyncio.create_task(playerhandler.playsplusone(datos["playerId"], "Beatleader", client))
                        if datos['country'] == os.getenv("pais") or str(datos["playerId"]) in jugadores.keys():
                            print(datos["player"]["name"])
                            print("Se registro un juego.")
                            playerhandler.updatelocalplayerdata(int(datos["playerId"]), datos)
        except Exception as e:
            print(e)