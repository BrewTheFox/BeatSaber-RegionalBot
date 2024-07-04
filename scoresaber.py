import requests
import discord
import json
import re
import websockets
import playerhandler
import beatsaver
import retos
import os

jugadores = playerhandler.fetchjugadores()
expresion = re.compile("https://scoresaber\.com/u/([0-9]*)")

def getplayerinfo(did:int) -> list:
    jugadores = playerhandler.fetchjugadores()
    for jugador in jugadores.keys():
        if str(jugadores[jugador]["discord"]) == str(did):
            datos = json.loads(requests.get(f"https://scoresaber.com/api/player/{jugador}/full").text)
            embed = discord.Embed(title=f"¡Perfil de {datos['name']}!", color=discord.Color.green())
            embed.set_thumbnail(url=datos['profilePicture'])
            embed.add_field(name="🌎", value=f"#{datos['rank']}", inline=True)
            code_points = [127397 + ord(char) for char in datos['country'].upper()]
            embed.add_field(name=''.join(chr(code) for code in code_points), value=f'#{datos["countryRank"]}', inline=True)
            embed.add_field(name="PP:", value=str(datos["pp"]), inline=False)
            embed.add_field(name="Puntaje total:", value=str('{:20,.0f}'.format(datos["scoreStats"]["totalScore"])), inline=False)
            embed.add_field(name="Juegos totales:", value=str(datos["scoreStats"]["totalPlayCount"]), inline=False)
            embed.add_field(name="Fecha de registro:", value=str(datos["firstSeen"]), inline=False)
            embed.set_footer(text="Bot por @brewthefox :D")
            return embed, False
    embed = discord.Embed(title="¡No hay una cuenta de scoresaber vinculada a este usuario!", color=discord.Color.red())
    embed.add_field(name="**Si la consulta es para ti usa /vincular, si es para otro usuario pidele que vincule su cuenta.**", value=" ")
    return embed, True

### Funciones de vinculacion con scoresaber ###
def vincular(link:str, uid:int):
    jugadores = playerhandler.fetchjugadores()
    link = link.replace("www.", "")
    if not link:
        embed = discord.Embed(title="No se puede vincular la cuenta sin un link valido.", color=discord.Color.red())
        return embed
    elif not link.startswith("https://scoresaber.com/u/"):
        embed = discord.Embed(title="Este servicio no se encuentra disponible, porfavor, solo scoresaber.", color=discord.Color.red())
        return embed
    else:
        id = expresion.findall(link)[0]
        url = f"https://scoresaber.com/api/player/{id}/full"
        response = requests.request("GET", url)
        if '"errorMessage"' in response.text:
            embed = discord.Embed(title="La cuenta introducida es invalida ;( intentalo denuevo.", color=discord.Color.red())
            return embed
        else:
            datos = json.loads(response.text)
            for jugador in jugadores.keys():
                if jugadores[jugador]["discord"] == str(uid):
                    embed = discord.Embed(title="Ya vinculaste una cuenta antes, si quieres vincular esta utiliza /desvincular primero.", color=discord.Color.red())
                    return embed
            if not id in jugadores.keys():
                embed = discord.Embed(title=f"Hola, {datos['name']} ¡Bienvenido!", color=discord.Color.green())
                embed.add_field(name="Fuiste registrado correctamente.", value=" ")
                embed.set_thumbnail(url=datos["profilePicture"])
                jugadores[str(id)] = {"discord":str(uid), "reto": {}}
                playerhandler.setjugadores(jugadores)
                return embed
            else:
                embed = discord.Embed(title="¿A quien engañas?", color=discord.Color.red())
                embed.add_field(name="Esta cuenta esta registrada por otro usuario", value=" ")
                return embed
            
def desvincular(uid:int):
    jugadores = playerhandler.fetchjugadores()
    encontrado = False
    for usuario in jugadores:
        if jugadores[usuario]['discord'] == str(uid):
            user = usuario
            encontrado = True
            del jugadores[usuario]
            playerhandler.setjugadores(jugadores)
            break
    if encontrado == True:
        url = f"https://scoresaber.com/api/player/{user}/full"
        response = requests.request("GET", url)
        datos = json.loads(response.text)
        embed = discord.Embed(title=f"La cuenta {datos['name']} se ha desvinculado de tu discord.", color=discord.Color.green())
        embed.set_thumbnail(url=datos["profilePicture"])
    else:
        embed = discord.Embed(title=f"No tienes una cuenta que desvincular.", color=discord.Color.red())
    return embed

async def recibir(client):
    print(client.guilds)
    jugadas = 0
    while True:
        try:
            async with websockets.connect("wss://scoresaber.com/ws") as socket:
                while True:
                    datos = await socket.recv()
                    if datos and "{" in datos:
                        datos = json.loads(datos)
                        jugadores = playerhandler.fetchjugadores()
                        if datos["commandData"]["score"]['leaderboardPlayerInfo']['country'] == os.getenv("pais") or str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]) in jugadores.keys():
                            print("Se encontro un jugador.")
                            nombre = datos['commandData']['score']['leaderboardPlayerInfo']['name']
                            gameid = datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]
                            pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
                            nombrecancion = datos["commandData"]["leaderboard"]["songName"]
                            imagenalbum = datos["commandData"]["leaderboard"]["coverImage"]
                            puntajemod = datos["commandData"]["score"]["modifiedScore"]
                            puntajebase = datos["commandData"]["score"]["baseScore"]
                            pp = datos["commandData"]["score"]["pp"]
                            estrellas = datos["commandData"]["leaderboard"]["stars"]
                            puntajemaximo = datos["commandData"]["leaderboard"]["maxScore"]
                            hashcancion = datos["commandData"]["leaderboard"]["songHash"]
                            dificultad = datos["commandData"]["leaderboard"]["difficulty"]["difficultyRaw"]
                            fallos = int(datos["commandData"]["score"]["badCuts"]) + int(datos["commandData"]["score"]["missedNotes"])
                            esvalido = [False, 0]
                            cancion = beatsaver.songinfo(hashcancion, dificultad)
                            if gameid in jugadores:
                                if len(jugadores[gameid]["reto"]) >= 1:
                                    esvalido = retos.validarreto(gameid, datos, jugadores)
                                    if esvalido[0] == True:
                                        retoembed = discord.Embed(title=f"¡Muy bien {nombre}, Lograste superar el reto")
                                        retoembed.add_field(name="Categoria", value=list(jugadores[gameid]["reto"].keys())[0].upper(), inline=False)
                                        retoembed.add_field(name="Valor a superar:", value=jugadores[gameid]["reto"][list(jugadores[gameid]["reto"].keys())[0]], inline=False)
                                        retoembed.add_field(name="Valor obtenido: ", value=esvalido[1], inline=False)
                                        retoembed.set_thumbnail(url=pfp)
                                        del jugadores[gameid]["reto"][list(jugadores[gameid]["reto"].keys())[0]]
                                        playerhandler.setjugadores(jugadores)
                            embed = discord.Embed(
                        title=f"¡**{nombre}** Logro!",
                        color=discord.Color.green()
                        )
                            embed.add_field(
                        name=f"Pasarse satisfactoriamente **{nombrecancion}**",
                        value=" ",
                        inline=False
                    )
                            embed.set_thumbnail(url=pfp)
                            embed.set_image(url=imagenalbum)
                            embed.add_field(
                            name="Puntaje: ",
                            value='{:20,.0f}'.format(puntajemod),
                            inline=False
                    )
                            embed.add_field(
                            name="PP añadido: ",
                            value=str(int(pp * datos["commandData"]["score"]["weight"])),
                            inline=True
                    )
                            if puntajemaximo != 0:
                                embed.add_field(name="Exactitud (Calculada):", value=str(round((puntajebase / puntajemaximo) * 100, 2)) + "%")
                            embed.add_field(name="Estrellas: ", value=str(estrellas))
                            if not "error" in cancion.keys():
                                embed.add_field(name="Notas logradas:", value=str(cancion["notas"] - fallos) + "/" + str(cancion["notas"]), inline=False)
                                embed.add_field(name="Dificultad:", value=cancion["dificultad"])
                            embed.add_field(name="Dispositivo: ", value=datos["commandData"]["score"]["deviceHmd"], inline=False)
                            embed.add_field(name="Control derecho:", value=datos["commandData"]["score"]["deviceControllerRight"])
                            embed.add_field(name="Control Izquierdo:", value=datos["commandData"]["score"]["deviceControllerLeft"])
                            if not "error" in cancion.keys():
                                embed.add_field(name="Descarga de la cancion:", value=(f"Utiliza [Este link](https://beatsaver.com/maps/{cancion['codigo']})"), inline=False)
                            embed.set_footer(text="El anterior juego de alguien de tu pais fue hace " + str(jugadas) + " partidas. Saludos @brewthefox")
                    
                            for guild in client.guilds:
                                for canal in guild.text_channels:
                                    if canal.name == "scoresaber":
                                        await canal.send(embed=embed)
                                    if canal.name == "retos" and esvalido[0] == True:
                                        await canal.send(embed=retoembed)
                            jugadas = 0
                        else:
                            jugadas += 1
                            actividad = discord.Game(f"Hace {str(jugadas)} juegos se registro el ultimo score de tu pais. ¡Se el siguiente en jugar!", type=1)
                            await client.change_presence(status=discord.Status.idle, activity=actividad)
        except Exception as e: 
            try:
                print("Ocurrio un error, reestableciendo")
                print(e)
                print("Datos importantes:")
                print(f"Nombre del jugador: {nombre}")
                print(f"ID del juego: {gameid}")
                print(f"Imagen de perfil: {pfp}")
                print(f"Nombre de la canción: {nombrecancion}")
                print(f"Imagen del álbum: {imagenalbum}")
                print(f"Puntaje obtenido: {puntajebase}")
                print(f"Puntos de rendimiento (pp): {pp}")
                print(f"Dificultad: {estrellas}")
                print(f"Puntaje máximo posible: {puntajemaximo}")
                print(f"Es válido: {esvalido[0]}, Código de validez: {esvalido[1]}")
            except:
                print("No existen datos para mostrar")
