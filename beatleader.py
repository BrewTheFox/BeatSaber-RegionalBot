import websockets
import playerhandler
import json
import aiohttp
import discord
import asyncio
import logging
import DataBaseManager
from loadconfig import GetString, GetConfiguration
from Embeds import PlayerEmbed, ErrorWithFieldsEmbed

async def GetPlayerInfo(did:int) -> list:
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(did)
    if player:
        async with session as ses:
            async with ses.get(f"https://api.beatleader.xyz/player/{player.id}?stats=true&keepOriginalId=false") as request:
                data = json.loads(await request.text())
                await session.close()
        embed = PlayerEmbed(discord.Color.purple(), data)
    embed = ErrorWithFieldsEmbed(GetString("AskUserToLink", "Misc"), [{"name":GetString("NoLinkedAccountUser", "Misc"), "value":" "}])
    return embed, True


async def Recieve(client:discord.Client):
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
                        if datos['country'] == GetConfiguration()['Country'] or DataBaseManager.LoadPlayerID(str(datos["playerId"])):
                            logging.info(f"Se registro un Juego del jugador {datos["player"]["name"]}")
                            playerhandler.UpdateLocalPlayerData(int(datos["playerId"]), datos)
        except Exception as e:
            logging.error(e)