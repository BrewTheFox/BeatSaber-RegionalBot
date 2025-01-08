import discord
import aiohttp
import asyncio
import re
import logging
import DataBaseManager
import challenges
from Embeds import ScoreEmbed, ChallengeEmbed, OvercomeEmbed
import scoresaber
import beatleader

HMDs = {"256": "Quest 2",    "512": "Quest 3",    "64": "Valve Index",    "513": "Quest 3S",    "1": "Rift CV1",    "2": "Vive",    "60": "Pico 4",    "61": "Quest Pro",    "70": "PS VR2",    "8": "Windows Mixed Reality",    "16": "Rift S",    "65": "Controllable",    "32": "Quest",    "4": "Vive Pro",    "35": "Vive Pro 2",    "128": "Vive Cosmos",    "36": "Vive Elite",    "47": "Vive Focus",    "38": "Pimax 8K",    "39": "Pimax 5K",    "40": "Pimax Artisan",    "33": "Pico Neo 3",    "34": "Pico Neo 2",    "41": "HP Reverb",    "42": "Samsung WMR",    "43": "Qiyu Dream",    "45": "Lenovo Explorer",    "46": "Acer WMR",    "66": "Bigscreen Beyond",    "67": "NOLO Sonic",    "68": "Hypereal",    "48": "Arpara",    "49": "Dell Visor",    "71": "MeganeX VG1",    "55": "Huawei VR",    "56": "Asus WMR",    "51": "Vive DVT",    "52": "glasses20",    "53": "Varjo",    "69": "Varjo Aero",    "54": "Vaporeon",    "57": "Cloud XR",    "58": "VRidge",    "50": "e3",    "59": "Medion Eraser",    "37": "Miramar",    "0": "Unknown headset",    "44": "Disco"}

async def SendOvercomeEmbed(overcameplayer:list, client:discord.Client, playername:str, playerid:str, pfp:str, platform:str):
    if overcameplayer[0]:
        Oembed, Obuttons = OvercomeEmbed(overcameplayer[1], overcameplayer[2], playername, playerid, pfp, overcameplayer[3], overcameplayer[4], platform)
        for guild in DataBaseManager.GetChannels(2):
            try:
                channel = client.get_channel(int(guild[0]))
                await channel.send(embed=Oembed, view=Obuttons)
            except Exception as e:
                print(e)
                DataBaseManager.RemoveChannel(guild[0])


async def UpdateList():
    """Syncs the HMDs list with the one in the beatleader github """
    global HMDs
    session = aiohttp.ClientSession()
    while True:
        logging.info("Actualizando HMDs")
        logging.info(f"Antes de: {len(HMDs.keys())}")
        try:
            DataExpresion = re.compile(r"([0-9]*): {\s*name: '(.*)'") #El codigo de BeatLeader para los HMDs esta en un formato en el cual no encontre una forma de parsear, por lo que en la posicion 1 que da el id del headset y en la posicion 2 su nombre, 0 es toda la expresion
            TempHMDs = {}
            async with session as ses:
                async with ses.get("https://raw.githubusercontent.com/BeatLeader/beatleader-website/refs/heads/master/src/utils/beatleader/format.js") as request:
                    data = await request.text()
            headsets = DataExpresion.finditer(data)
            for headset in headsets:
                TempHMDs[headset[1]] = headset[2]
            HMDs = TempHMDs
        except Exception as e:
            logging.error(e)
        await session.close()
        logging.info(f"Despues de: {len(HMDs.keys())}")
        await asyncio.sleep(10000)

async def PostEmbeds(*, datos:dict, client: discord.Client, gamestill:int):
    values = [False, 0]

    if "Beatleader" in datos.keys():
        playerid = str(datos["player"]["id"])
        playername = datos["player"].get("name")
        puntajemod = datos["contextExtensions"][0]["modifiedScore"]
        pp = datos["contextExtensions"][0]["pp"]
        pfp = datos["player"]["avatar"]
        estrellas = round(datos["leaderboard"]["difficulty"].get("stars") or 0, 2)
        weight = datos["contextExtensions"][0]["weight"]
        overcameplayer = await beatleader.GetPlayerPassedOther(pp * weight, str(playerid))
        await SendOvercomeEmbed(overcameplayer, client, playername, playerid, pfp, "Beatleader")
    if "Scoresaber" in datos.keys():
        playerid = str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"])
        playername = datos['commandData']['score']['leaderboardPlayerInfo'].get('name')
        puntajemod = datos["commandData"]["score"]["modifiedScore"]
        pp = datos["commandData"]["score"]["pp"]
        estrellas = datos["commandData"]["leaderboard"]["stars"]
        weight = datos["commandData"]["score"]["weight"]
        overcameplayer = await scoresaber.GetPlayerPassedOther(pp * weight, str(playerid))
        pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
        await SendOvercomeEmbed(overcameplayer, client, playername, playerid, pfp, "Scoresaber")

    challenge = DataBaseManager.GetChallenge(playerid)
    if challenge[0]:
        values = challenges.CheckChallenge(playerid, pp, estrellas, puntajemod)
        retoembed = ChallengeEmbed(datos, challenge[0], challenge[1], playerid, values)
    
    embed, buttons = await ScoreEmbed(datos, HMDs, gamestill)

    for guild in DataBaseManager.GetChannels(1):
        try:
            channel = client.get_channel(int(guild[0]))
            await channel.send(embed=embed, view=buttons)
        except Exception as e:
            print(e)
            DataBaseManager.RemoveChannel(guild[0])
        for guild in DataBaseManager.GetChannels(0):
            if values[0] == True:
                try:
                    channel = client.get_channel(int(guild[0]))
                    await channel.send(embed=retoembed)
                except Exception as e:
                    print(e)
                    DataBaseManager.RemoveChannel(guild[0])