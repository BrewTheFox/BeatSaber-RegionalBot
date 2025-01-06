import discord
import time
import scoreembed
import aiohttp
import json
import re
import asyncio
import logging
import classes
import DataBaseManager

plays = 0
pdata = {}
lpdata = {}
expresionss = re.compile("https://scoresaber\\.com/u/([0-9]*)")
expresionbl = re.compile("https://beatleader\\.xyz/u/([0-9]*)")

async def CheckLocalPlayerData(client:discord.Client):
    global lpdata
    clpdata = dict(lpdata)
    for jugador in clpdata.keys():
        if clpdata[jugador]["timesregistered"] == 1 and clpdata[jugador]["time"] < time.time():
            logging.info("No se esta jugando doble")
            try:
                del lpdata[jugador]
            except NameError:
                continue
            asyncio.create_task(scoreembed.postembed(datos=clpdata[jugador]["gameplayinfo"], client=client, gamestill=plays))
            ResetPlays()
        elif clpdata[jugador]["time"] > time.time():
            continue
        else:
            logging.info("Se esta jugando doble")
            try:
                del lpdata[jugador]
            except NameError:
                continue
            asyncio.create_task(scoreembed.postembed(datos=clpdata[jugador]["gameplayinfo"], client=client, gamestill=plays))
            ResetPlays()

def ResetPlays() -> None:
    global plays
    plays = 0

def UpdateLocalPlayerData(playerid:int, datos:dict):
    global lpdata
    playerid = str(playerid)
    if not playerid in list(lpdata.keys()):
        lpdata[playerid] = {"time":time.time() + 6, "timesregistered":1, "gameplayinfo": datos}
    else:
        if lpdata[playerid]["gameplayinfo"].get("Scoresaber") != datos.get("Scoresaber") or lpdata[playerid]["gameplayinfo"].get("Beatleader") != datos.get("Beatleader"):
            lpdata[playerid]["timesregistered"] += 1
            lpdata[playerid]["gameplayinfo"].update(datos)

async def PlaysPlusOne(playerid:int, leaderboard:str, client:discord.Client) -> None:
    global plays
    global pdata
    playerid = str(playerid)
    copypdata = dict(pdata)
    if not playerid in list(pdata.keys()):
        pdata[playerid] = {"time":time.time(), "leaderboard":leaderboard}
    for datos in copypdata:
        if copypdata[datos]["time"] + 6 < time.time() or copypdata[datos]["leaderboard"] is leaderboard:
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


async def Link(link:str, uid:int):
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(str(uid))

    if player:
        embed = discord.Embed(title="Ya vinculaste una cuenta antes, si quieres vincular esta utiliza /desvincular primero.", color=discord.Color.red())
        return embed
    
    link = link.replace("www.", "")
    if not link:
        embed = discord.Embed(title="No se puede vincular la cuenta sin un link valido.", color=discord.Color.red())
        return embed
    
    if link.startswith("https://scoresaber.com/u/") or link.startswith("https://beatleader.xyz/u/"):
        if link.startswith("https://scoresaber.com/u/"):
            id = expresionss.findall(link)[0]
            url = f"https://scoresaber.com/api/player/{id}/full"
        if link.startswith("https://beatleader.xyz/u/"):
            id = expresionbl.findall(link)[0]
            url = f"https://api.beatleader.xyz/player/{id}?stats=false&keepOriginalId=false"

        async with session as ses:
            async with ses.get(url) as request:
                response = await request.text()
                status = request.status
                await session.close()

        if not '"errorMessage"' in response or status == 404:
            datos = json.loads(response)
            if DataBaseManager.LoadPlayerID(str(id)):
                embed = discord.Embed(title="¿A quien engañas?", color=discord.Color.red())
                embed.add_field(name="Esta cuenta esta registrada por otro usuario", value=" ")
                return embed
            else:
                embed = discord.Embed(title=f"Hola, {datos['name']} ¡Bienvenido!", color=discord.Color.green())
                embed.add_field(name="Fuiste registrado correctamente.", value=" ")
                if link.startswith("https://beatleader.xyz/u/"):
                    embed.set_thumbnail(url=datos["avatar"])
                if link.startswith("https://scoresaber.com/u/"):
                    embed.set_thumbnail(url=datos["profilePicture"])
                DataBaseManager.InsertPlayer(classes.player(id=str(id), discord=str(uid), challenge=None, total_points=0, points=None))
                return embed
            
        else:
            embed = discord.Embed(title="La cuenta introducida es invalida ;( intentalo denuevo.", color=discord.Color.red())
            return embed
    else:
        embed = discord.Embed(title="Este servicio no se encuentra disponible, porfavor, solo scoresaber o beatleader.", color=discord.Color.red())
        return embed

            
async def Unlink(uid:int):
    session = aiohttp.ClientSession()
    player = DataBaseManager.LoadPlayerDiscord(str(uid))
    if player:
        url = f"https://scoresaber.com/api/player/{player.id}/full"
        async with session as ses:
            async with ses.get(url) as request:
                datos = json.loads(await request.text())
        embed = discord.Embed(title=f"La cuenta {datos['name']} se ha desvinculado de tu discord.", color=discord.Color.green())
        embed.set_thumbnail(url=datos["profilePicture"])
    else:
        embed = discord.Embed(title=f"No tienes una cuenta que desvincular.", color=discord.Color.red())
    return embed
