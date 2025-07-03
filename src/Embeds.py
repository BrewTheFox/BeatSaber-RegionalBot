import discord
from loadconfig import GetString, GetConfiguration
import logging
import buttonViews
import beatsaver as beatsaver

def PlayerEmbed(color:discord.Colour, data:dict) -> discord.Embed:
    embed = discord.Embed(title=GetConfiguration()["Strings"]["ProfileRequest"]["ProfileOf"].replace("{{name}}", data["name"]), color=color)
    embed.set_thumbnail(url=data.get('avatar') or data.get('profilePicture'))
    embed.add_field(name="🌎", value=f"#{data['rank']}", inline=True)
    code_points = [127397 + ord(char) for char in data['country'].upper()]
    embed.add_field(name=''.join(chr(code) for code in code_points), value=f'#{data["countryRank"]}', inline=True)
    embed.add_field(name=GetString("PerformancePoints"), value=str(data["pp"]), inline=False)
    embed.add_field(name=GetString("TotalScore"), value=str('{:20,.0f}'.format(data["scoreStats"]["totalScore"])), inline=False)
    embed.add_field(name=GetString("TotalPlays"), value=str(data["scoreStats"]["totalPlayCount"]), inline=False)
    return embed

def ErrorWithFieldsEmbed(title:str, fields:list):
    embed = discord.Embed(title=title, color=discord.Color.red())
    for field in fields:
        embed.add_field(name=field["name"], value=field["value"])
    return embed

def ErrorEmbed(title:str):
    embed = discord.Embed(title=title, color=discord.Color.red())
    return embed

def SuccessEmbed(title:str):
    embed = discord.Embed(title=title, color=discord.Color.green())
    return embed

def OvercomeEmbed(OvercomedName:str, OvercomedID:str, OvercomerName:str, OvercomerID:str, OvercomerPFP:str, DiffPoints:float, leaderboardposition:str, platform:str):
    buttons = buttonViews.Buttons()
    embed = discord.Embed(title=GetString("OvercomeTitle", "Overcome").replace("{{name1}}", OvercomerName).replace("{{name2}}", OvercomedName), color=discord.Color.blurple())
    DiffPoints = f'{int(DiffPoints):,}'
    leaderboardposition = f'{int(leaderboardposition):,}'
    embed.add_field(name=GetString("OvercomeDescription", "Overcome").replace("{{var1}}", DiffPoints).replace("{{var2}}", leaderboardposition).replace("{{leaderboard}}", platform), value=" ")
    embed.set_thumbnail(url=OvercomerPFP)
    if platform == "Scoresaber":
        buttons.AddButton(OvercomedName, "https://scoresaber.com/u/" + OvercomedID, GetString("ScoreSaberEmoji", "ScoreEmbed"))
        buttons.AddButton(OvercomerName, "https://scoresaber.com/u/" + OvercomerID, GetString("ScoreSaberEmoji", "ScoreEmbed"))
    else:
        buttons.AddButton(OvercomedName, "https://beatleader.com/u/" + OvercomedID, GetString("BeatLeaderEmoji", "ScoreEmbed"))
        buttons.AddButton(OvercomerName, "https://beatleader.com/u/" + OvercomerID, GetString("BeatLeaderEmoji", "ScoreEmbed"))
    return embed, buttons

def ChallengeEmbed(datos:dict, challenge:str, points:str, playerid:str, values:list):
    if "Scoresaber" in datos.keys() and "Beatleader" in datos.keys():
        playername = datos['commandData']['score']['leaderboardPlayerInfo'].get('name')
        pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
    if "Beatleader" in datos.keys() and not "Scoresaber" in datos.keys():
        playername = datos["player"].get("name")
        pfp = datos["player"]["avatar"]
    if "Scoresaber" in datos.keys() and not "Beatleader" in datos.keys():
        playername = datos['commandData']['score']['leaderboardPlayerInfo']['name']
        pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]

    embed = discord.Embed(title=GetString("UserCompletedChallenge", "Challenges").replace("{{name}}", playername))
    embed.add_field(name=GetString("Category", "Challenges"), value=challenge.title(), inline=False)
    embed.add_field(name=GetString("OvercomeValue", "Challenges"), value=points, inline=False)
    embed.add_field(name=GetString("ObtainedValue", "Challenges"), value=values[1], inline=False)
    embed.set_thumbnail(url=pfp)
    return embed


async def ScoreEmbed(datos:dict, HMDs:dict, gamestill:int):
    buttons = buttonViews.Buttons()
    if "Scoresaber" in datos.keys() and "Beatleader" in datos.keys():
        try:
            plataforma = "ScoreSaber y Beatleader"
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
            pp = datos["commandData"]["score"]["pp"], datos["pp"]
            estrellas = round(max([datos["commandData"]["leaderboard"]["stars"], datos["leaderboard"]["difficulty"]["stars"] or 0]), 2)
            weight = datos["commandData"]["score"]["weight"], datos["contextExtensions"][0]["weight"]
            puntajemaximo = datos["commandData"]["leaderboard"]["maxScore"]
            hashcancion = datos["commandData"]["leaderboard"].get("songHash")
            dificultad = datos["commandData"]["leaderboard"]["difficulty"]["difficultyRaw"]
            fallos = int(datos["commandData"]["score"]["badCuts"]) + int(datos["commandData"]["score"]["missedNotes"])
            replay = "https://replay.beatleader.com/?scoreId=" + str(datos["id"])
            buttons.AddButton(f"{playername} Beatleader", f"https://beatleader.com/u/{playerid}", GetString("BeatLeaderEmoji", "ScoreEmbed"))
            buttons.AddButton(f"{playername} Scoresaber", f"https://scoresaber.com/u/{playerid}", GetString("ScoreSaberEmoji", "ScoreEmbed"))
            cancion = await beatsaver.songinfo(hashcancion, dificultad)
        except Exception as e:
            logging.error(f"Ocurrio un {e} Al momento de asignar las variables multiples para el jugador {playername}")
    if "Beatleader" in datos.keys() and not "Scoresaber" in datos.keys():
        try:
            plataforma = "Beatleader"
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
            puntajemod = datos["modifiedScore"]
            puntajebase = datos["baseScore"]
            pp = datos["pp"]
            weight = datos["weight"]
            estrellas = round(datos["leaderboard"]["difficulty"]["stars"] or 0, 2)
            puntajemaximo = datos["leaderboard"]["difficulty"]["maxScore"]
            fallos = (abs(datos["badCuts"]) + abs(datos["missedNotes"]))
            replay = "https://replay.beatleader.com/?scoreId=" + str(datos["id"])
            cancion = await beatsaver.songinfo(hashcancion, f"_{dificultad}_{modo}")
            buttons.AddButton(playername, f"https://beatleader.com/u/{playerid}", GetString("BeatLeaderEmoji", "ScoreEmbed"))
        except Exception as e:
            logging.error(f"Ocurrio un {e} Al momento de asignar las variables de BeatLeader para el jugador {playername}")
    if "Scoresaber" in datos.keys() and not "Beatleader" in datos.keys():
        try:
            plataforma = "ScoreSaber"
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
            cancion = await beatsaver.songinfo(hashcancion, dificultad)
            buttons.AddButton(playername, f"https://scoresaber.com/u/{playerid}", GetString("ScoreSaberEmoji", "ScoreEmbed"))
        except Exception as e:
            logging.error(f"Ocurrio un error {e} Al momento de asignar las variables de ScoreSaber para el jugador {playername}")
    dificultad = (cancion["dificultad"]).replace("Plus", "+")
    datos_keys = datos.keys()
    embed = discord.Embed(title=GetString("EmbedTitle", "ScoreEmbed").replace("{{name}}", playername), color=color)
    embed.add_field(name=GetString("ToPass", "ScoreEmbed").replace("{{song}}", nombrecancion).replace("{{difficulty}}", dificultad),value=" ",inline=False)
    embed.set_thumbnail(url=pfp)
    embed.set_image(url=imagenalbum)
    embed.add_field(name=GetString("Score", "ScoreEmbed"),value='{:20,.0f}'.format(puntajemod),inline=True)

    if plataforma == "ScoreSaber" or plataforma == "Beatleader":
        embed.add_field(name=GetString("AddedPerformancePoints", "ScoreEmbed"),value=str(round(float(pp * weight),2)),inline=True)
    else:
        embed.add_field(name=GetString("AddedPerformancePointsBeatLeader", "ScoreEmbed"),value=str(round(float(pp[1] * weight[1]), 2)),inline=True)
        embed.add_field(name=GetString("AddedPerformancePointsScoreSaber", "ScoreEmbed"),value=str(round(float(pp[0] * weight[0]), 2)),inline=True)

    if puntajemaximo != 0:
        embed.add_field(name=GetString("Average", "ScoreEmbed"), value=str(round((puntajebase / puntajemaximo) * 100, 2)) + "%", inline=True)
        embed.add_field(name=GetString("Stars", "ScoreEmbed"), value=str(estrellas) + "★", inline=True)

        if not "error" in cancion.keys():
            embed.add_field(name=GetString("GoodvsWrong", "ScoreEmbed"), value=str(cancion["notas"] - fallos) + "/" + str(cancion["notas"]), inline=True)
        if "Scoresaber" in datos_keys:
            hmd += f'({datos["commandData"]["score"]["deviceControllerRight"]})'

        embed.add_field(name=GetString("Device", "ScoreEmbed"), value=hmd, inline=True)
        embed.add_field(name=GetString("Platform", "ScoreEmbed"), value=plataforma, inline=True)

        if "replay" in datos_keys:
            buttons.AddButton(GetString("ViewReplay", "ScoreEmbed"), replay, "<a:bspepe:1368253102880329808>")

        if not "error" in cancion.keys():
            buttons.AddButton(GetString("DownloadSong", "ScoreEmbed"), f"https://beatsaver.com/maps/{cancion['codigo']}", GetString("BeatSaverEmoji", "ScoreEmbed"))
        embed.set_footer(text=GetString("LastGameBefore", "ScoreEmbed").replace("{{var}}", str(gamestill)))
    return embed, buttons