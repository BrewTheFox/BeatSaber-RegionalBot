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
from math import ceil

COUNTRY = GetConfiguration()['Country']

async def GetPlayerInfo(did:int) -> list:
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(did)
    if player:
        async with session as ses:
            async with ses.get(f"https://api.beatleader.xyz/player/{player.id}?stats=true&keepOriginalId=false") as request:
                data = json.loads(await request.text())
        embed = PlayerEmbed(discord.Color.purple(), data)
        return embed, False
    embed = ErrorWithFieldsEmbed(GetString("AskUserToLink", "Misc"), [{"name":GetString("NoLinkedAccountUser", "Misc"), "value":" "}])
    return embed, True

async def GetPlayerPassedOther(addedPP:int, PlayerID:str):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://api.beatleader.xyz/player/{PlayerID}?stats=true&keepOriginalId=false") as request:
            playerinfo = json.loads(await request.text())
    CurrentRank = playerinfo["countryRank"]
    Page = int(ceil(CurrentRank / 50))
    Specific = CurrentRank - (Page - 1) * 49

    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://api.beatleader.xyz/players?leaderboardContext=general&page={Page}&count=50&sortBy=pp&mapsType=ranked&ppType=general&order=desc&countries={COUNTRY}&pp_range=%2C&score_range=%2C") as request:
            data = json.loads(await request.text())
    PPBefore = data["data"][Specific]["pp"] - addedPP
    if Specific != len(data["data"]) - 1:
        PPAdversarial = data["data"][Specific + 1]["pp"]
    else:
        async with aiohttp.ClientSession() as ses:
            async with ses.get(f"https://api.beatleader.xyz/players?leaderboardContext=general&page={Page + 1}&count=50&sortBy=pp&mapsType=ranked&ppType=general&order=desc&countries={COUNTRY}&pp_range=%2C&score_range=%2C") as request:
                data = json.loads(await request.text())
        try:
            PPAdversarial = data["data"][0]["pp"]
        except:
            return [False, None, 0, 0, "0"]
    if PPAdversarial < PPBefore or playerinfo["country"] != COUNTRY:
        return [False, None, 0, 0, "0"]
    logging.info(f"El usuario {PlayerID} supero al usuario {data["data"][Specific + 1]["id"]}")
    return [True, data["data"][Specific + 1]["name"], data["data"][Specific + 1]["id"], PPAdversarial - PPBefore, str(CurrentRank)]

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
                        if datos['country'] == COUNTRY or DataBaseManager.LoadPlayerID(str(datos["playerId"])):
                            logging.info(f"Se registro un Juego del jugador {datos["player"]["name"]}")
                            playerhandler.UpdateLocalPlayerData(int(datos["playerId"]), datos)
        except Exception as e:
            logging.error(e)