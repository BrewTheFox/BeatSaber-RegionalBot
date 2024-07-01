import requests
import discord
import json
import re
import saveapi

expresion = re.compile("https://scoresaber\.com/u/([0-9]*)")

def getplayerinfo(did:int, jugadores:dict) -> list:
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