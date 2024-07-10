import discord
import beatsaver
import saveapi
import playerhandler
import retos

async def postembed(*, datos:dict, client, gamestill:int):
    print("Scoresaber" in datos.keys() and not "Beatleader" in datos.keys())
    if "Scoresaber" in datos.keys() and "Beatleader" in datos.keys():
        print("Variables multiples asignadas")
        nombre = datos['commandData']['score']['leaderboardPlayerInfo']['name']
        gameid = str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"])
        pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
        nombrecancion = datos["commandData"]["leaderboard"]["songName"]
        imagenalbum = datos["commandData"]["leaderboard"]["coverImage"]
        puntajemod = datos["commandData"]["score"]["modifiedScore"]
        puntajebase = datos["commandData"]["score"]["baseScore"]
        pp = max([datos["commandData"]["score"]["pp"], datos["contextExtensions"][0]["pp"]])
        estrellas = round(max([datos["commandData"]["leaderboard"]["stars"], datos["leaderboard"]["difficulty"]["stars"] or 0]), 2)
        weight = datos["commandData"]["score"]["weight"]
        puntajemaximo = datos["commandData"]["leaderboard"]["maxScore"]
        hashcancion = datos["commandData"]["leaderboard"]["songHash"]
        dificultad = datos["commandData"]["leaderboard"]["difficulty"]["difficultyRaw"]
        fallos = int(datos["commandData"]["score"]["badCuts"]) + int(datos["commandData"]["score"]["missedNotes"])
        replay = datos["replay"]
        plataforma = "ScoreSaber y Beatleader"
        cancion = beatsaver.songinfo(hashcancion, dificultad)
    if "Beatleader" in datos.keys() and not "Scoresaber" in datos.keys():
        print("Iniciando variables de beatleader")
        nombre = datos["player"]["name"]
        gameid = str(datos["player"]["id"])
        pfp = datos["player"]["avatar"]
        hashcancion = datos["leaderboard"]["song"]["hash"]
        dificultad = datos["leaderboard"]["difficulty"]["difficultyName"]
        modo = datos["leaderboard"]["difficulty"]["modeName"]
        cancion = beatsaver.songinfo(hashcancion, f"_{dificultad}_{modo}")
        nombrecancion = cancion["nombre"]
        imagenalbum = cancion["imagen"]
        puntajemod = datos["contextExtensions"][0]["modifiedScore"]
        puntajebase = datos["contextExtensions"][0]["baseScore"]
        pp = datos["contextExtensions"][0]["pp"]
        weight = datos["contextExtensions"][0]["weight"]
        estrellas = datos["leaderboard"]["difficulty"]["stars"] or 0
        puntajemaximo = datos["leaderboard"]["difficulty"]["maxScore"]
        fallos = int(datos["scoreImprovement"]["badCuts"] + datos["scoreImprovement"]["missedNotes"])
        replay = datos["replay"]
        plataforma = "Beatleader"
    if "Scoresaber" in datos.keys() and not "Beatleader" in datos.keys():
        print("Variables scoresaber asignadas")
        nombre = datos['commandData']['score']['leaderboardPlayerInfo']['name']
        gameid = str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"])
        pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
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
        cancion = beatsaver.songinfo(hashcancion, dificultad)
        plataforma = "ScoreSaber"
    esvalido = [False, 0]
    jugadores = saveapi.loadplayers()
    if gameid in jugadores:
        if len(jugadores[gameid]["reto"]) >= 1:
            esvalido = retos.validarreto(gameid, pp, estrellas, puntajemod)
            if esvalido[0] == True:
                retoembed = discord.Embed(title=f"¡Muy bien {nombre}, Lograste superar el reto")
                retoembed.add_field(name="Categoria", value=list(jugadores[gameid]["reto"].keys())[0].upper(), inline=False)
                retoembed.add_field(name="Valor a superar:", value=jugadores[gameid]["reto"][list(jugadores[gameid]["reto"].keys())[0]], inline=False)
                retoembed.add_field(name="Valor obtenido: ", value=esvalido[1], inline=False)
                retoembed.set_thumbnail(url=pfp)
                del jugadores[gameid]["reto"][list(jugadores[gameid]["reto"].keys())[0]]
                playerhandler.setjugadores(jugadores)

    embed = discord.Embed(title=f"¡**{nombre}** Logro!",color=discord.Color.green())
    embed.add_field(name=f"Pasarse satisfactoriamente **{nombrecancion}**",value=" ",inline=False)
    embed.set_thumbnail(url=pfp)
    embed.set_image(url=imagenalbum)
    embed.add_field(name="Puntaje: ",value='{:20,.0f}'.format(puntajemod),inline=False)
    embed.add_field(name="PP añadido: ",value=str(int(pp * weight)),inline=True)
    if puntajemaximo != 0:
        embed.add_field(name="Exactitud (Calculada):", value=str(round((puntajebase / puntajemaximo) * 100, 2)) + "%")
        embed.add_field(name="Estrellas: ", value=str(estrellas))
        if not "error" in cancion.keys():
            embed.add_field(name="Notas logradas:", value=str(cancion["notas"] - fallos) + "/" + str(cancion["notas"]))
            embed.add_field(name="Dificultad:", value=cancion["dificultad"])
        if "Scoresaber" in datos.keys():
            embed.add_field(name="Dispositivo: ", value=datos["commandData"]["score"]["deviceHmd"], inline=False)
            embed.add_field(name="Control derecho:", value=datos["commandData"]["score"]["deviceControllerRight"])
            embed.add_field(name="Control Izquierdo:", value=datos["commandData"]["score"]["deviceControllerLeft"])
        embed.add_field(name="Plataforma", value=plataforma, inline=False)
        if "replay" in datos.keys():
            embed.add_field(name="Ver el replay:", value=f"Utiliza [Este link]({replay})", inline=False)
        if not "error" in cancion.keys():
            embed.add_field(name="Descarga de la cancion:", value=(f"Utiliza [Este link](https://beatsaver.com/maps/{cancion['codigo']})"), inline=False)
        embed.set_footer(text="El anterior juego de alguien de tu pais fue hace " + str(gamestill) + " partidas. Saludos @brewthefox")
        for guild in client.guilds:
                for canal in guild.text_channels:
                    if canal.name == "livescores":
                        await canal.send(embed=embed)
                    if canal.name == "retos" and esvalido[0] == True:
                        await canal.send(embed=retoembed)