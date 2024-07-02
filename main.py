import websockets
import json
import discord
from typing import Literal
from dotenv import load_dotenv
import os
import beatsaver
import saveapi
import scoresaber
import retos

load_dotenv("./config.env")
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
print("Cargando usuarios...")

jugadores = saveapi.loadplayers()

@tree.command(name="bsperfil", description="Obtiene datos de tu perfil de scoresaber")
async def obtenerdatos(interaction: discord.Interaction):
    global jugadores
    embed, efimero = scoresaber.getplayerinfo(interaction.user.id, jugadores)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="verperfil", description="Obtiene datos del perfil de scoresaber de alguien del servidor")
async def obtenerjugador(interaction: discord.Interaction, miembro:discord.Member):
    global jugadores
    embed, efimero = scoresaber.getplayerinfo(miembro.id, jugadores)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="desvincular", description="Desvincula y elimina los datos de la cuenta.")
async def desvincular(interaction: discord.Interaction):
    global jugadores
    embed, jugadores = scoresaber.desvincular(interaction.user.id, jugadores)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="cancelar", description="Cancela el reto actual.")
async def cancelar(interaction: discord.Interaction):
    global jugadores
    embed, jugadores = retos.cancelarreto(interaction.user.id, jugadores)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="reto", description="Asigna un reto dentro del juego.")
async def retar(interaction: discord.Interaction, dificultad: Literal["Facil", "Dificil", "Expert+"]):
    global jugadores
    embed, jugadores = retos.generarreto(interaction.user.id, dificultad, jugadores)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="vincular", description="Vincula una cuenta de scoresaber con tu cuenta de discord.")
async def vincular(interaction: discord.Interaction, link:str):
    global jugadores
    embed, jugadores = scoresaber.vincular(link, jugadores, interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def recibir():
    print(client.guilds)
    jugadas = 0
    while True:
        try:
            async with websockets.connect("wss://scoresaber.com/ws") as socket:
                while True:
                    datos = await socket.recv()
                    if datos and "{" in datos:
                        datos = json.loads(datos)
                        if datos["commandData"]["score"]['leaderboardPlayerInfo']['country'] == os.getenv("pais") or str(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]) in jugadores.keys():
                            print("Se encontro un jugador.")
                            nombre = datos['commandData']['score']['leaderboardPlayerInfo']['name']
                            gameid = datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]
                            pfp = datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"]
                            nombrecancion = datos["commandData"]["leaderboard"]["songName"]
                            imagenalbum = datos["commandData"]["leaderboard"]["coverImage"]
                            puntaje = datos["commandData"]["score"]["modifiedScore"]
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
                                        saveapi.guardarjugadores(jugadores)
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
                            value='{:20,.0f}'.format(puntaje),
                            inline=False
                    )
                            embed.add_field(
                            name="PP añadido: ",
                            value=str(int(pp * datos["commandData"]["score"]["weight"])),
                            inline=True
                    )
                            if puntajemaximo != 0:
                                embed.add_field(name="Exactitud (Calculada):", value=str(round((puntaje / puntajemaximo) * 100, 2)) + "%")
                            embed.add_field(name="Estrellas: ", value=str(estrellas))
                            if not "error" in cancion.keys():
                                embed.add_field(name="Notas logradas:", value=str(cancion["notas"] - fallos) + "/" + str(cancion["notas"]), inline=False)
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
                print(f"Puntaje obtenido: {puntaje}")
                print(f"Puntos de rendimiento (pp): {pp}")
                print(f"Dificultad: {estrellas}")
                print(f"Puntaje máximo posible: {puntajemaximo}")
                print(f"Es válido: {esvalido[0]}, Código de validez: {esvalido[1]}")
            except:
                print("No existen datos para mostrar")

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    try:
        synced = await tree.sync()
        print(f"Se sincronizaron {str(len(synced))} comandos")
    except Exception as e:
        print(e)

    client.loop.create_task(recibir())

client.run(os.getenv("token"))
