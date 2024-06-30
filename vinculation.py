import requests
import discord
import re
import json
import saveapi
expresion = re.compile("https://scoresaber\.com/u/([0-9]*)")

def vincular(link:str, jugadores:dict, uid:int) -> list:
    link = link.replace("www.", "")
    if not link:
        embed = discord.Embed(title="No se puede vincular la cuenta sin un link valido.", color=discord.Color.red())
        return embed, jugadores
    elif not link.startswith("https://scoresaber.com/u/"):
        embed = discord.Embed(title="Este servicio no se encuentra disponible, porfavor, solo scoresaber.", color=discord.Color.red())
        return embed, jugadores
    else:
        id = expresion.findall(link)[0]
        url = f"https://scoresaber.com/api/player/{id}/full"
        response = requests.request("GET", url)
        if '"errorMessage"' in response.text:
            embed = discord.Embed(title="La cuenta introducida es invalida ;( intentalo denuevo.", color=discord.Color.red())
            return embed, jugadores
        else:
            datos = json.loads(response.text)
            if not id in jugadores.keys():
                embed = discord.Embed(title=f"Hola, {datos['name']} ¡Bienvenido!", color=discord.Color.green())
                embed.add_field(name="Fuiste registrado correctamente.", value=" ")
                embed.set_thumbnail(url=datos["profilePicture"])
                jugadores[str(id)] = {"discord":str(uid), "reto": {}}
                saveapi.guardarjugadores(jugadores)
                return embed, jugadores
            else:
                embed = discord.Embed(title="¿A quien engañas?", color=discord.Color.red())
                embed.add_field(name="Esta cuenta esta registrada por otro usuario", value=" ")
                return embed, jugadores
            
def desvincular(uid:int, jugadores: dict) -> list:
    encontrado = False
    for usuario in jugadores:
        if jugadores[usuario]['discord'] == str(uid):
            user = usuario
            encontrado = True
            del jugadores[usuario]
            saveapi.guardarjugadores(jugadores)
            break
    if encontrado == True:
        url = f"https://scoresaber.com/api/player/{user}/full"
        response = requests.request("GET", url)
        datos = json.loads(response.text)
        embed = discord.Embed(title=f"La cuenta {datos['name']} se ha desvinculado de tu discord.", color=discord.Color.green())
        embed.set_thumbnail(url=datos["profilePicture"])
    else:
        embed = discord.Embed(title=f"No tienes una cuenta que desvincular.", color=discord.Color.red())
    return embed, jugadores