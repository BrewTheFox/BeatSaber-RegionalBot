import saveapi
import discord
import time
import scoreembed
import playerhandler
import requests
import json
import re
jugadores = saveapi.loadplayers()
plays = 0
pdata = {}
lpdata = {}
expresionss = re.compile("https://scoresaber\.com/u/([0-9]*)")
expresionbl = re.compile("https://beatleader\.xyz/u/([0-9]*)")
def updatelocalplayerdata(playerid:int, datos:dict):
    global lpdata
    playerid = str(playerid)
    if not playerid in list(lpdata.keys()):
        lpdata[playerid] = {"time":time.time(), "timesregistered":1, "gameplayinfo": datos}
    else:
        lpdata[playerid]["timesregistered"] += 1
        lpdata[playerid]["gameplayinfo"].update(datos)


async def checklocalplayerdata(client):
    global lpdata
    clpdata = dict(lpdata)
    for jugador in clpdata.keys():
        if clpdata[jugador]["timesregistered"] == 1 and clpdata[jugador]["time"] + 4 < time.time():
            print("No se esta jugando doble")
            try:
                del lpdata[jugador]
            except:
                continue
            await scoreembed.postembed(datos=clpdata[jugador]["gameplayinfo"], client=client, gamestill=plays)
            resetplays()
        elif clpdata[jugador]["time"] + 4 > time.time() and clpdata[jugador]["timesregistered"] == 1:
            print("Esperando...")
        else:
            print("Se esta jugando doble")
            try:
                del lpdata[jugador]
            except:
                continue
            await scoreembed.postembed(datos=clpdata[jugador]["gameplayinfo"], client=client, gamestill=plays)
            resetplays()
def fetchjugadores() -> dict:
    return jugadores

def setjugadores(newjugadores:dict) -> dict:
    global jugadores
    jugadores = newjugadores
    saveapi.guardarjugadores(jugadores)
    return jugadores

def resetplays() -> None:
    global plays
    plays = 0

def fetchplays() -> int:
    global plays
    return plays

async def playsplusone(playerid:int, leaderboard:str, client) -> None:
    global plays
    global pdata
    playerid = str(playerid)
    copypdata = dict(pdata)
    if not playerid in list(pdata.keys()):
        pdata[playerid] = {"time":time.time(), "leaderboard":leaderboard}
    for datos in copypdata:
        if copypdata[datos]["time"] + 4 < time.time() or copypdata[datos]["leaderboard"] is leaderboard:
            plays += 1
            actividad = discord.Game(f"Hace {str(plays)} juegos se registro el ultimo score de tu pais. ¡Se el siguiente en jugar!", type=1)
            await client.change_presence(status=discord.Status.idle, activity=actividad)
            if datos in pdata.keys():
                del pdata[datos]
        else:
            plays += 1
            actividad = discord.Game(f"Hace {str(plays)} juegos se registro el ultimo score de tu pais. ¡Se el siguiente en jugar!", type=1)
            await client.change_presence(status=discord.Status.idle, activity=actividad)
            if datos in pdata.keys():
                del pdata[datos]

def vincular(link:str, uid:int):
    jugadores = playerhandler.fetchjugadores()
    link = link.replace("www.", "")
    if not link:
        embed = discord.Embed(title="No se puede vincular la cuenta sin un link valido.", color=discord.Color.red())
        return embed
    elif not link.startswith("https://scoresaber.com/u/") and not link.startswith("https://beatleader.xyz/u/"):
        embed = discord.Embed(title="Este servicio no se encuentra disponible, porfavor, solo scoresaber o beatleader.", color=discord.Color.red())
        return embed
    else:
        if link.startswith("https://scoresaber.com/u/"):
            id = expresionss.findall(link)[0]
            url = f"https://scoresaber.com/api/player/{id}/full"
        if link.startswith("https://beatleader.xyz/u/"):
            id = expresionbl.findall(link)[0]
            url = f"https://api.beatleader.xyz/player/{id}?stats=false&keepOriginalId=false"

        response = requests.request("GET", url)
        if '"errorMessage"' in response.text or response.status_code == 404:
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
                if link.startswith("https://beatleader.xyz/u/"):
                    embed.set_thumbnail(url=datos["avatar"])
                if link.startswith("https://scoresaber.com/u/"):
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