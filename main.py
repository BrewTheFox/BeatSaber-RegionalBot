import websockets
import json
import discord
import requests
import re
from typing import Literal
import random
import csv
from dotenv import load_dotenv
import os

load_dotenv("./config.env")
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
expresion = re.compile("https://scoresaber\.com/u/([0-9]*)")
jugadores = {}
headers = ['id', 'discord', 'reto', 'puntos']
print("Cargando usuarios...")

with open("./save.csv", "r") as archivo:
    lector = csv.reader(archivo, delimiter=",")
    headers = next(lector)
    cantidadusuarios = 0
    for row in lector:
        cantidadusuarios += 1
        id = row[0]
        ds = row[1]
        reto = row[2]
        cantidad = row[3]
        if not id in jugadores:
            jugadores[id] = {"discord":ds, 'reto':{}}
        if reto != "NULL":
            jugadores[id]['reto'][reto] = int(cantidad)

print(str(cantidadusuarios) + " Usuarios cargados.")

def guardarjugadores():
    with open("./save.csv", "w") as archivo:
        escritor = csv.writer(archivo, delimiter=",")
        escritor.writerow(headers)
        for id_jugador, datos in jugadores.items():
            if datos['reto']:
                for tipo, cantidad in datos['reto'].items():
                    fila = [id_jugador, datos['discord'], tipo, cantidad]
                    escritor.writerow(fila)
            else:
                fila = [id_jugador, datos['discord'], 'NULL', 'NULL']
                escritor.writerow(fila)
    print("Jugadores guardados.")


def validarreto(id:str, datos):
    if list(jugadores[id]["reto"].keys())[0] == "pp":
        return [datos["commandData"]["score"]["pp"] >= jugadores[id]["reto"]["pp"], datos["commandData"]["score"]["pp"]]
    if list(jugadores[id]["reto"].keys())[0] == "estrellas":
        return [datos["commandData"]["leaderboard"]["stars"] >= jugadores[id]["reto"]["estrellas"], datos["commandData"]["leaderboard"]["stars"]]
    if list(jugadores[id]["reto"].keys())[0] == "puntaje":
        return [datos["commandData"]["score"]["modifiedScore"] >= jugadores[id]["reto"]["puntaje"], datos["commandData"]["score"]["modifiedScore"]]

@tree.command(name="desvincular", description="Desvincula y elimina los datos de la cuenta.")
async def desvincular(interaction: discord.Interaction):
    encontrado = False
    for usuario in jugadores:
        if jugadores[usuario]['discord'] == str(interaction.user.id):
            user = usuario
            encontrado = True
            del jugadores[usuario]
            guardarjugadores()
            break
    if encontrado == True:
        url = f"https://scoresaber.com/api/player/{user}/full"
        response = requests.request("GET", url)
        datos = json.loads(response.text)
        embed = discord.Embed(title=f"La cuenta {datos["name"]} se ha desvinculado de tu discord.", color=discord.Color.green())
        embed.set_thumbnail(url=datos["profilePicture"])
    else:
        embed = discord.Embed(title=f"No tienes una cuenta que desvincular.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="cancelar", description="Cancela el reto actual.")
async def cancelar(interaction: discord.Interaction):
    encontrado = False
    for jugador in jugadores.keys():
        if str(interaction.user.id) == jugadores[jugador]["discord"]:
            encontrado = True
            if len(list(jugadores[jugador]["reto"].keys())) >=1:
                del jugadores[jugador]["reto"][list(jugadores[jugador]["reto"].keys())[0]]
                embed = discord.Embed(title=f"Cancelaste tu reto :(", color=discord.Color.red())
                guardarjugadores()
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title=f"No has solicitado ningun reto :(", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)                
    if encontrado == False:    
        embed = discord.Embed(title=f"Si quieres usar este comando tendras que registrarte con /vincular <link>", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)    

@tree.command(name="reto", description="Asigna un reto dentro del juego.")
async def retar(interaction: discord.Interaction, dificultad: Literal["Facil", "Dificil", "Expert+"]):
    encontrado = False
    retos = ["puntaje", "estrellas", "pp"]
    for jugador in jugadores.keys():
        print(jugadores[jugador]["discord"] == str(interaction.user.id))
        if str(interaction.user.id) == jugadores[jugador]["discord"]:
            encontrado = True
            id = str(jugador)
            break
    if encontrado == True:
        if len(jugadores[id]["reto"].keys()) >= 1:
            embed = discord.Embed(title=f"¡Ya solicitaste un reto /cancelar si no lo quieres!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        tipo = random.choice(retos)
        if dificultad == "Facil":
            if tipo == "puntaje":
                puntaje = random.randint(150, 600) * 1000
                jugadores[id]["reto"][tipo] = puntaje
                embed = discord.Embed(title=f"¡Consigue mas de {puntaje} puntos en un nivel!", color=discord.Color.blue())
            if tipo == "estrellas":
                estrellas = random.randint(1,5)
                jugadores[id]["reto"][tipo] = estrellas
                embed = discord.Embed(title=f"¡Pasate un nivel de {estrellas} estrellas o mas!", color=discord.Color.blue())
            if tipo == "pp":
                cantidad = random.randint(10,100)
                jugadores[id]["reto"][tipo] = cantidad
                embed = discord.Embed(title=f"¡Pasate un nivel con mas de {cantidad} PP!", color=discord.Color.blue())
            guardarjugadores()
            await interaction.response.send_message(embed=embed)
        if dificultad == "Dificil":
            if tipo == "puntaje":
                puntaje = random.randint(600, 1200) * 1000
                jugadores[id]["reto"][tipo] = puntaje
                embed = discord.Embed(title=f"¡Consigue mas de {puntaje} puntos en un nivel!", color=discord.Color.green())
            if tipo == "estrellas":
                estrellas = random.randint(5,9)
                jugadores[id]["reto"][tipo] = estrellas
                embed = discord.Embed(title=f"¡Pasate un nivel de {estrellas} estrellas o mas!", color=discord.Color.green())
            if tipo == "pp":
                cantidad = random.randint(100,250)
                jugadores[id]["reto"][tipo] = cantidad
                embed = discord.Embed(title=f"¡Pasate un nivel con mas de {cantidad} PP!", color=discord.Color.green())
            guardarjugadores()
            await interaction.response.send_message(embed=embed)
        if dificultad == "Expert+":
            if tipo == "puntaje":
                puntaje = random.randint(1200, 2000) * 1000
                jugadores[id]["reto"][tipo] = puntaje
                embed = discord.Embed(title=f"¡Consigue mas de {puntaje} puntos en un nivel!", color=discord.Color.orange())
            if tipo == "estrellas":
                estrellas = random.randint(10,13)
                jugadores[id]["reto"][tipo] = estrellas
                embed = discord.Embed(title=f"¡Pasate un nivel de {estrellas} estrellas o mas!", color=discord.Color.orange())
            if tipo == "pp":
                cantidad = random.randint(400,550)
                jugadores[id]["reto"][tipo] = cantidad
                embed = discord.Embed(title=f"¡Pasate un nivel con mas de {cantidad} PP!", color=discord.Color.orange())
            guardarjugadores()
            await interaction.response.send_message(embed=embed)        
    else:
        embed = discord.Embed(title="Porfavor vincula tu cuenta con /vincular <link> para acceder a esta funcion.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
@tree.command(name="vincular", description="Vincula una cuenta de scoresaber con tu cuenta de discord.")
async def vincular(interaction: discord.Interaction, link:str):
    link = link.replace("www.", "")
    print(interaction.user.id)
    if not link:
        embed = discord.Embed(title="No se puede vincular la cuenta sin un link valido.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif not link.startswith("https://scoresaber.com/u/"):
        embed = discord.Embed(title="Este servicio no se encuentra disponible, porfavor, solo scoresaber.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        id = expresion.findall(link)[0]
        url = f"https://scoresaber.com/api/player/{id}/full"
        response = requests.request("GET", url)
        if '"errorMessage"' in response.text:
            embed = discord.Embed(title="La cuenta introducida es invalida ;( intentalo denuevo.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            datos = json.loads(response.text)
            if not id in jugadores.keys():
                embed = discord.Embed(title=f"Hola, {datos["name"]} ¡Bienvenido!", color=discord.Color.green())
                embed.add_field(name="Fuiste registrado correctamente.", value=" ")
                embed.set_thumbnail(url=datos["profilePicture"])
                jugadores[str(id)] = {"discord":str(interaction.user.id), "reto": {}}
                guardarjugadores()
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title="¿A quien engañas?", color=discord.Color.red())
                embed.add_field(name="Esta cuenta esta registrada por otro usuario", value=" ")
                await interaction.response.send_message(embed=embed, ephemeral=True)

async def recibir():
    print(client.guilds)
    jugadas = 0
    async with websockets.connect("wss://scoresaber.com/ws") as socket:
        while True:
            datos = await socket.recv()
            if datos and "{" in datos:
                datos = json.loads(datos)
                if datos["commandData"]["score"]['leaderboardPlayerInfo']['country'] == os.getenv("pais"):
                    esvalido = False
                    if datos["commandData"]["score"]['leaderboardPlayerInfo']["id"] in jugadores:
                        if len(jugadores[datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]]["reto"]) >= 1:
                            esvalido = validarreto(datos["commandData"]["score"]['leaderboardPlayerInfo']["id"], datos)
                            if esvalido[0] == True:
                                retoembed = discord.Embed(title=f"¡Muy bien {datos['commandData']['score']['leaderboardPlayerInfo']['name']}, Lograste superar el reto")
                                retoembed.add_field(name="Categoria", value=list(jugadores[datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]]["reto"].keys())[0].upper(), inline=False)
                                retoembed.add_field(name="Valor a superar:", value=jugadores[datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]]["reto"][list(jugadores[datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]]["reto"].keys())[0]], inline=False)
                                retoembed.add_field(name="Valor obtenido: ", value=esvalido[1], inline=False)
                                retoembed.set_thumbnail(url=datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"])
                                del jugadores[datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]]["reto"][list(jugadores[datos["commandData"]["score"]['leaderboardPlayerInfo']["id"]]["reto"].keys())[0]]
                                guardarjugadores()
                    embed = discord.Embed(
                        title=f"¡**{datos['commandData']['score']['leaderboardPlayerInfo']['name']}** Logro!",
                        color=discord.Color.green()
                        )
                    embed.add_field(
                        name="Pasarse satisfactoriamente **" + datos["commandData"]["leaderboard"]["songName"] + "**",
                        value=" ",
                        inline=False
                    )
                    embed.set_thumbnail(url=datos["commandData"]["score"]['leaderboardPlayerInfo']["profilePicture"])
                    embed.set_image(url=datos["commandData"]["leaderboard"]["coverImage"])
                    embed.add_field(
                        name="Puntaje: ",
                        value='{:20,.0f}'.format(datos["commandData"]["score"]["modifiedScore"]),
                        inline=False
                    )
                    embed.add_field(
                        name="PP añadido: ",
                        value=str(int(datos["commandData"]["score"]["pp"] * datos["commandData"]["score"]["weight"])),
                        inline=True
                    )
                    embed.add_field(name="Dispositivo: ", value=datos["commandData"]["score"]["deviceHmd"])
                    embed.add_field(name="Dificultad: ", value=str(datos["commandData"]["leaderboard"]["difficulty"]["difficulty"]), inline=False)
                    embed.set_footer(text="El anterior juego de un Colombiano fue hace " + str(jugadas) + " partidas. Saludos @brewthefox")
                    
                    for guild in client.guilds:
                        for canal in guild.text_channels:
                            if canal.name == "scoresaber":
                                await canal.send(embed=embed)
                            if canal.name == "retos" and esvalido[0] == True:
                                await canal.send(embed=retoembed)
                    jugadas = 0
                else:
                    jugadas += 1
                    print("Pais erroneo (" + datos["commandData"]["score"]['leaderboardPlayerInfo']['country'] + ") Jugadas: " + str(jugadas))

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