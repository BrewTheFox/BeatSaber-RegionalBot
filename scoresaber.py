import aiohttp
import discord
import json
import websockets
import playerhandler
import os
import asyncio
import logging
import DataBaseManager

async def GetPlayerInfo(did:int) -> list:
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(did)
    if player:
        async with session as ses:
            async with ses.get(f"https://scoresaber.com/api/player/{player.id}/full") as request:
                datos = json.loads(await request.text())
                await session.close()
        embed = discord.Embed(title=f"¡Perfil de {datos['name']}!", color=discord.Color.yellow())
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

async def recieve(client:discord.Client):
    while True:
        try:
            async with websockets.connect("wss://scoresaber.com/ws") as socket:
                while True:
                    data = await socket.recv()
                    if data and "{" in data:
                        await playerhandler.CheckLocalPlayerData(client)
                        data = json.loads(data)
                        if data.get("commandData"):
                            data["Scoresaber"] = True
                            if data["commandData"]["score"]['leaderboardPlayerInfo']['country'] == os.getenv("pais") or DataBaseManager.LoadPlayerID(str(data["commandData"]["score"]['leaderboardPlayerInfo']["id"])):
                                logging.info(f"Se registro un Juego del jugador {data['commandData']['score']['leaderboardPlayerInfo']['name']}")
                                playerid = data["commandData"]["score"]['leaderboardPlayerInfo']["id"]
                                playerhandler.UpdateLocalPlayerData(playerid, data)
                            else:
                                asyncio.create_task(playerhandler.PlaysPlusOne(data["commandData"]["score"]['leaderboardPlayerInfo']["id"], "scoresaber", client))
        except Exception as e: 
            logging.error(f"Se desconecto el websocket con el error {e}")
