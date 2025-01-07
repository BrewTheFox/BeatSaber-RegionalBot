import aiohttp
import discord
import json
import websockets
import playerhandler
import asyncio
import logging
import DataBaseManager
from embeds import PlayerEmbed, ErrorWithFieldsEmbed
from loadconfig import GetString, GetConfiguration

async def GetPlayerInfo(did:int) -> list:
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(did)
    if player:
        async with session as ses:
            async with ses.get(f"https://scoresaber.com/api/player/{player.id}/full") as request:
                data = json.loads(await request.text())
                await session.close()
        embed = PlayerEmbed(discord.Color.yellow, data)
        return embed, False
    
    embed = ErrorWithFieldsEmbed(GetString("AskUserToLink", "Misc"), [{"name":GetString("NoLinkedAccountUser", "Misc"), "value":" "}])
    return embed, True

async def Recieve(client:discord.Client):
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
                            if data["commandData"]["score"]['leaderboardPlayerInfo']['country'] == GetConfiguration()['Country'] or DataBaseManager.LoadPlayerID(str(data["commandData"]["score"]['leaderboardPlayerInfo']["id"])):
                                logging.info(f"Se registro un Juego del jugador {data['commandData']['score']['leaderboardPlayerInfo']['name']}")
                                playerid = data["commandData"]["score"]['leaderboardPlayerInfo']["id"]
                                playerhandler.UpdateLocalPlayerData(playerid, data)
                            else:
                                asyncio.create_task(playerhandler.PlaysPlusOne(data["commandData"]["score"]['leaderboardPlayerInfo']["id"], "scoresaber", client))
        except Exception as e: 
            logging.error(f"Se desconecto el websocket con el error {e}")
