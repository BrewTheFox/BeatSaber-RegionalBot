import aiohttp
import discord
import json
import websockets
import playerhandler as playerhandler
import asyncio
import logging
import DataBaseManager as DataBaseManager
from Embeds import PlayerEmbed, ErrorWithFieldsEmbed
from loadconfig import GetString, GetConfiguration

COUNTRY = GetConfiguration()['Country']

async def GetPlayerInfo(did:int) -> list:
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(did)
    if player:
        async with session as ses:
            async with ses.get(f"https://scoresaber.com/api/player/{player[0]}/full") as request:
                data = json.loads(await request.text())
        embed = PlayerEmbed(discord.Color.yellow(), data)
        return embed, False
    embed = ErrorWithFieldsEmbed(GetString("AskUserToLink", "Misc"), [{"name":GetString("NoLinkedAccountUser", "Misc"), "value":" "}])
    return embed, True

async def GetPlayerPassedOther(PlayerID:str):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://scoresaber.com/api/player/{PlayerID}/full") as request:
            playerinfo = json.loads(await request.text())

    DataBaseManager.InsertTopPlayer(0, PlayerID, playerinfo["pp"]) # Take into account that 0 = ScoreSaber
    OldPP = DataBaseManager.GetPlayerPP(0, PlayerID)
    PlayersPassed = DataBaseManager.GetPlayersBetween(0, OldPP[0], playerinfo["pp"])
    if PlayerID in PlayersPassed:
        PlayersPassed = list(PlayersPassed).remove(PlayerID)
    if len(PlayersPassed) <= 1 or PlayersPassed == None:
        return [False, None, 0, 0, "0"]
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://scoresaber.com/api/player/{PlayersPassed[-1][0]}/full") as request:
            adversarialinfo = json.loads(await request.text())
    DataBaseManager.UpdatePlayerPerformancePoints(0, PlayerID, playerinfo["pp"])
    return [True, adversarialinfo["name"], adversarialinfo["id"], adversarialinfo["pp"] - playerinfo["pp"], str(playerinfo["countryRank"])]

async def Recive(client:discord.Client):
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
