import aiohttp
import discord
import json
import websockets
import playerhandler
import asyncio
import logging
import DataBaseManager
from Embeds import PlayerEmbed, ErrorWithFieldsEmbed
from loadconfig import GetString, GetConfiguration
from math import ceil

COUNTRY = GetConfiguration()['Country']

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

async def GetPlayerPassedOther(addedPP:int, PlayerID:str):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://scoresaber.com/api/player/{PlayerID}/full") as request:
            playerinfo = json.loads(await request.text())
    CurrentRank = playerinfo["countryRank"]
    Page = int(ceil(CurrentRank / 50))
    Specific = CurrentRank - (Page - 1) * 50 - 1

    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://scoresaber.com/api/players?countries={COUNTRY}&page={Page}") as request:
            data = json.loads(await request.text())
    PPBefore = data["players"][Specific]["pp"] - addedPP
    if Specific != len(data["players"]) - 1:
        PPAdversarial = data["players"][Specific + 1]["pp"]
    else:
        async with aiohttp.ClientSession() as ses:
            async with ses.get(f"https://scoresaber.com/api/players?countries={COUNTRY}&page={Page + 1}") as request:
                data = json.loads(await request.text())
        try:
            PPAdversarial = data["players"][0]["pp"]
        except:
            return [False, None, 0, 0]
    if PPAdversarial < PPBefore:
        return [False, None, 0, 0]
    return [True, data["players"][Specific + 1]["name"], data["players"][Specific + 1]["id"], PPAdversarial - PPBefore]


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
                            if data["commandData"]["score"]['leaderboardPlayerInfo']['country'] == COUNTRY or DataBaseManager.LoadPlayerID(str(data["commandData"]["score"]['leaderboardPlayerInfo']["id"])):
                                logging.info(f"Se registro un Juego del jugador {data['commandData']['score']['leaderboardPlayerInfo']['name']}")
                                playerid = data["commandData"]["score"]['leaderboardPlayerInfo']["id"]
                                playerhandler.UpdateLocalPlayerData(playerid, data)
                            else:
                                asyncio.create_task(playerhandler.PlaysPlusOne(data["commandData"]["score"]['leaderboardPlayerInfo']["id"], "scoresaber", client))
        except Exception as e: 
            logging.error(f"Se desconecto el websocket con el error {e}")
