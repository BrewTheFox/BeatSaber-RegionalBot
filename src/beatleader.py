import websockets
import playerhandler as playerhandler
import json
import aiohttp
import discord
import asyncio
import logging
import DataBaseManager as DataBaseManager
from loadconfig import GetString, GetConfiguration
from Embeds import PlayerEmbed, ErrorWithFieldsEmbed
from math import ceil

COUNTRY = GetConfiguration()['Country']

async def GetPlayerInfo(did:int) -> list:
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(did)
    if player:
        async with session as ses:
            async with ses.get(f"https://api.beatleader.com/player/{player[0]}?stats=true&keepOriginalId=false") as request:
                data = json.loads(await request.text())
        embed = PlayerEmbed(discord.Color.purple(), data)
        return embed, False
    embed = ErrorWithFieldsEmbed(GetString("AskUserToLink", "Misc"), [{"name":GetString("NoLinkedAccountUser", "Misc"), "value":" "}])
    return embed, True

async def GetPlayerPassedOther(PlayerID:str):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://api.beatleader.com/player/{PlayerID}?keepOriginalId=false") as request:
            playerinfo = json.loads(await request.text())

    DataBaseManager.InsertTopPlayer(1, PlayerID, playerinfo["pp"]) # Take into account that 1 = BeatLeader
    OldPP = DataBaseManager.GetPlayerPP(1, PlayerID)
    PlayersPassed = DataBaseManager.GetPlayersBetween(1, OldPP[0], playerinfo["pp"])
    PlayersPassed = list(PlayersPassed)
    if PlayerID in PlayersPassed:
        PlayersPassed.remove(PlayerID)
    if PlayerID == PlayersPassed[-1]:
        PlayersPassed.pop(-1)
    if len(PlayersPassed) < 1 or PlayersPassed == None:
        return [False, None, 0, 0, "0"]
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://api.beatleader.com/player/{PlayersPassed[-1][0]}?keepOriginalId=false") as request:
            adversarialinfo = json.loads(await request.text())
    DataBaseManager.UpdatePlayerPerformancePoints(1, PlayerID, playerinfo["pp"])
    return [True, adversarialinfo["name"], adversarialinfo["id"], playerinfo["pp"] - adversarialinfo["pp"], str(playerinfo["countryRank"])]


async def Recive(client:discord.Client):
    while True:
        try:
            async with websockets.connect("wss://sockets.api.beatleader.com/scores") as socket:
                while True:
                    datos = await socket.recv()
                    if datos and "{" in datos:
                        await playerhandler.CheckLocalPlayerData(client)
                        datos = json.loads(datos)
                        datos["Beatleader"] = True
                        asyncio.create_task(playerhandler.PlaysPlusOne(datos["playerId"], "Beatleader", client))
                        if datos['country'] == COUNTRY or DataBaseManager.LoadPlayerID(str(datos["playerId"])):
                            logging.info(f"Se registro un Juego del jugador {datos["player"]["name"]}")
                            playerhandler.UpdateLocalPlayerData(int(datos["playerId"]), datos)
        except Exception as e:
            logging.error(e)