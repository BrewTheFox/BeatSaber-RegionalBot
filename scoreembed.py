import discord
import beatsaver
import challenges
import aiohttp
import asyncio
import re
import logging
import DataBaseManager
import classes
from loadconfig import GetString

HMDs = {"256": "Quest 2",    "512": "Quest 3",    "64": "Valve Index",    "513": "Quest 3S",    "1": "Rift CV1",    "2": "Vive",    "60": "Pico 4",    "61": "Quest Pro",    "70": "PS VR2",    "8": "Windows Mixed Reality",    "16": "Rift S",    "65": "Controllable",    "32": "Quest",    "4": "Vive Pro",    "35": "Vive Pro 2",    "128": "Vive Cosmos",    "36": "Vive Elite",    "47": "Vive Focus",    "38": "Pimax 8K",    "39": "Pimax 5K",    "40": "Pimax Artisan",    "33": "Pico Neo 3",    "34": "Pico Neo 2",    "41": "HP Reverb",    "42": "Samsung WMR",    "43": "Qiyu Dream",    "45": "Lenovo Explorer",    "46": "Acer WMR",    "66": "Bigscreen Beyond",    "67": "NOLO Sonic",    "68": "Hypereal",    "48": "Arpara",    "49": "Dell Visor",    "71": "MeganeX VG1",    "55": "Huawei VR",    "56": "Asus WMR",    "51": "Vive DVT",    "52": "glasses20",    "53": "Varjo",    "69": "Varjo Aero",    "54": "Vaporeon",    "57": "Cloud XR",    "58": "VRidge",    "50": "e3",    "59": "Medion Eraser",    "37": "Miramar",    "0": "Unknown headset",    "44": "Disco"}

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


async def PostEmbed(*, datos:dict, client: discord.Client, gamestill:int):
    """Esta funcion solo genera el embed, se encarga principalmente de bindear los datos necesarios a variables
    Y es casi insostenible, para generar al final solo un embed que requiere de unas 20 lineas de codigo .-."""
    buttons = classes.Buttons()
    if "Scoresaber" in datos.keys() and "Beatleader" in datos.keys():
        try:
            color = discord.Color.dark_orange()
            playername = datos['commandData']['score']['leaderboardPlayerInfo'].get('name')
            logging.debug(f"Variables multiples asignadas para el usuario {playername}")
            playerid = str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"])
            pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
            nombrecancion = datos["commandData"]["leaderboard"]["songName"]
            imagenalbum = datos["commandData"]["leaderboard"]["coverImage"]
            puntajemod = datos["commandData"]["score"]["modifiedScore"]
            puntajebase = datos["commandData"]["score"]["baseScore"]
            hmd = HMDs[str(datos["hmd"])]
            pp = max([datos["commandData"]["score"]["pp"], datos["contextExtensions"][0]["pp"]])
            estrellas = round(max([datos["commandData"]["leaderboard"]["stars"], datos["leaderboard"]["difficulty"]["stars"] or 0]), 2)
            weight = max(datos["commandData"]["score"]["weight"], datos["contextExtensions"][0]["weight"])
            puntajemaximo = datos["commandData"]["leaderboard"]["maxScore"]
            hashcancion = datos["commandData"]["leaderboard"].get("songHash")
            dificultad = datos["commandData"]["leaderboard"]["difficulty"]["difficultyRaw"]
            fallos = int(datos["commandData"]["score"]["badCuts"]) + int(datos["commandData"]["score"]["missedNotes"])
            replay = datos["replay"]
            plataforma = "ScoreSaber y Beatleader"
            buttons.AddButton(f"{playername} Beatleader", f"https://beatleader.com/u/{playerid}")
            buttons.AddButton(f"{playername} Scoresaber", f"https://scoresaber.com/u/{playerid}")

        except Exception as e:
            logging.error(f"Ocurrio un {e} Al momento de asignar las variables multiples para el jugador {playername}")
    if "Beatleader" in datos.keys() and not "Scoresaber" in datos.keys():
        try:
            color = discord.Color.dark_purple()
            playername = datos["player"].get("name")
            logging.debug(f"Variables Beatleader asignadas para el usuario {playername}")
            playerid = str(datos["player"]["id"])
            hmd = HMDs[str(datos["hmd"])]
            pfp = datos["player"]["avatar"]
            hashcancion = datos["leaderboard"]["song"].get("hash")
            dificultad = datos["leaderboard"]["difficulty"]["difficultyName"]
            modo = datos["leaderboard"]["difficulty"]["modeName"]
            nombrecancion = datos["leaderboard"]["song"]["name"]
            imagenalbum = datos["leaderboard"]["song"]["coverImage"]
            puntajemod = datos["contextExtensions"][0]["modifiedScore"]
            puntajebase = datos["contextExtensions"][0]["baseScore"]
            pp = datos["contextExtensions"][0]["pp"]
            weight = datos["contextExtensions"][0]["weight"]
            estrellas = round(datos["leaderboard"]["difficulty"]["stars"] or 0, 2)
            puntajemaximo = datos["leaderboard"]["difficulty"]["maxScore"]
            fallos = - int(datos["scoreImprovement"]["badCuts"] + datos["scoreImprovement"]["missedNotes"])
            replay = datos["replay"]
            plataforma = "Beatleader"
            buttons.AddButton(playername, f"https://beatleader.com/u/{playerid}")
        except Exception as e:
            logging.error(f"Ocurrio un {e} Al momento de asignar las variables de BeatLeader para el jugador {playername}")
    if "Scoresaber" in datos.keys() and not "Beatleader" in datos.keys():
        try:
            color = discord.Color.gold()
            playername = datos['commandData']['score']['leaderboardPlayerInfo']['name']
            logging.debug(f"Variables ScoreSaber asignadas para el usuario {playername}")
            playerid = str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"])
            pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
            hmd = datos["commandData"]["score"]["deviceHmd"]
            nombrecancion = datos["commandData"]["leaderboard"]["songName"]
            imagenalbum = datos["commandData"]["leaderboard"]["coverImage"]
            puntajemod = datos["commandData"]["score"]["modifiedScore"]
            puntajebase = datos["commandData"]["score"]["baseScore"]
            pp = datos["commandData"]["score"]["pp"]
            weight = datos["commandData"]["score"]["weight"]
            estrellas = datos["commandData"]["leaderboard"]["stars"]
            puntajemaximo = datos["commandData"]["leaderboard"]["maxScore"]
            hashcancion = datos["commandData"]["leaderboard"]["songHash"]
            dificultad = datos["commandData"]["leaderboard"]["difficulty"]["difficultyRaw"]
            fallos = int(datos["commandData"]["score"]["badCuts"]) + int(datos["commandData"]["score"]["missedNotes"])
            plataforma = "ScoreSaber"
            buttons.AddButton(playername, f"https://scoresaber.com/u/{playerid}")
        except Exception as e:
            logging.error(f"Ocurrio un error {e} Al momento de asignar las variables de ScoreSaber para el jugador {playername}")
    values = [False, 0]

    challenge = DataBaseManager.GetChallenge(playerid)
    if challenge[0]:
        challenge, points, _ = challenge
        values = challenges.CheckChallenge(playerid, pp, estrellas, puntajemod)
        if values[0] == True:
            retoembed = discord.Embed(title=GetString("UserCompletedChallenge", "Challenges").replace("{{name}}", playername))
            retoembed.add_field(name=GetString("Category", "Challenges"), value=challenge.title(), inline=False)
            retoembed.add_field(name=GetString("OvercomeValue", "Challenges"), value=points, inline=False)
            retoembed.add_field(name=GetString("ObtainedValue", "Challenges"), value=values[1], inline=False)
            retoembed.set_thumbnail(url=pfp)
            DataBaseManager.CompleteChallenge(playerid)

    embed = discord.Embed(title=GetString("EmbedTitle", "ScoreEmbed").replace("{{name}}", playername), color=color)
    embed.add_field(name=GetString("ToPass", "ScoreEmbed").replace("{{song}}", nombrecancion),value=" ",inline=False)
    embed.set_thumbnail(url=pfp)
    embed.set_image(url=imagenalbum)
    embed.add_field(name=GetString("Score", "ScoreEmbed"),value='{:20,.0f}'.format(puntajemod),inline=False)
    embed.add_field(name=GetString("AddedPerformancePoints", "ScoreEmbed"),value=str(int(pp * weight)),inline=True)
    if puntajemaximo != 0:
        embed.add_field(name=GetString("Average", "ScoreEmbed"), value=str(round((puntajebase / puntajemaximo) * 100, 2)) + "%")
        embed.add_field(name=GetString("Stars", "ScoreEmbed"), value=str(estrellas))

        cancion = await beatsaver.songinfo(hashcancion, f"_{dificultad}_{modo}")
        if not "error" in cancion.keys():
            embed.add_field(name=GetString("GoodvsWrong", "ScoreEmbed"), value=str(cancion["notas"] - fallos) + "/" + str(cancion["notas"]))
            embed.add_field(name=GetString("Difficulty", "ScoreEmbed"), value=cancion["dificultad"])
        embed.add_field(name=GetString("Device", "ScoreEmbed"), value=hmd, inline=False)

        if "Scoresaber" in datos.keys():
            embed.add_field(name=GetString("RightController", "ScoreEmbed"), value=datos["commandData"]["score"]["deviceControllerRight"])
            embed.add_field(name=GetString("LeftController", "ScoreEmbed"), value=datos["commandData"]["score"]["deviceControllerLeft"])
        embed.add_field(name=GetString("Platform", "ScoreEmbed"), value=plataforma, inline=False)

        if "replay" in datos.keys():
            buttons.AddButton(GetString("ViewReplay", "ScoreEmbed"), replay)

        if not "error" in cancion.keys():
            buttons.AddButton(GetString("DownloadSong", "ScoreEmbed"), f"https://beatsaver.com/maps/{cancion['codigo']}")
        embed.set_footer(text=GetString("LastGameBefore", "ScoreEmbed").replace("{{var}}", str(gamestill)))

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