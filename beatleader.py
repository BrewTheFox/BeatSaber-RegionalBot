import websockets
import playerhandler
import json
import os
import aiohttp
import discord
import asyncio
import logging
import DataBaseManager

async def GetPlayerInfo(did:int) -> list:
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(did)
    if player:
        async with session as ses:
            async with ses.get(f"https://api.beatleader.xyz/player/{player.id}?stats=true&keepOriginalId=false") as request:
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
                    datos = await socket.recv()
                    if datos and "{" in datos:
                        await playerhandler.CheckLocalPlayerData(client)
                        datos = json.loads(datos)
                        datos["Beatleader"] = True
                        asyncio.create_task(playerhandler.PlaysPlusOne(datos["playerId"], "Beatleader", client))
                        if datos['country'] == os.getenv("pais") or DataBaseManager.LoadPlayerID(str(datos["playerId"])):
                            logging.info(f"Se registro un Juego del jugador {datos["player"]["name"]}")
                            playerhandler.UpdateLocalPlayerData(int(datos["playerId"]), datos)
        except Exception as e:
            logging.error(e)