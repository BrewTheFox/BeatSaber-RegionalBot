import discord
import random
import playerhandler


def validarreto(id:str, datos:dict) -> list:
    jugadores = playerhandler.fetchjugadores()
    if list(jugadores[id]["reto"].keys())[0] == "pp":
        return [datos["commandData"]["score"]["pp"] >= jugadores[id]["reto"]["pp"], datos["commandData"]["score"]["pp"]]
    if list(jugadores[id]["reto"].keys())[0] == "estrellas":
        return [datos["commandData"]["leaderboard"]["stars"] >= jugadores[id]["reto"]["estrellas"], datos["commandData"]["leaderboard"]["stars"]]
    if list(jugadores[id]["reto"].keys())[0] == "puntaje":
        return [datos["commandData"]["score"]["modifiedScore"] >= jugadores[id]["reto"]["puntaje"], datos["commandData"]["score"]["modifiedScore"]]

def generarreto(uid:int, dificultad:str):
    jugadores = playerhandler.fetchjugadores()
    encontrado = False
    retos = ["puntaje", "estrellas", "pp"]
    for jugador in jugadores.keys():
        print(jugadores[jugador]["discord"] == str(uid))
        if str(uid) == jugadores[jugador]["discord"]:
            encontrado = True
            id = str(jugador)
            break
    if encontrado == True:
        if len(jugadores[id]["reto"].keys()) >= 1:
            embed = discord.Embed(title=f"¡Ya solicitaste un reto /cancelar si no lo quieres!", color=discord.Color.red())
            return embed
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
            playerhandler.setjugadores(jugadores)
            return embed
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
            playerhandler.setjugadores(jugadores)
            return embed
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
            playerhandler.setjugadores(jugadores)
            return embed
    else:
        embed = discord.Embed(title="Porfavor vincula tu cuenta con /vincular <link> para acceder a esta funcion.", color=discord.Color.red())
        return embed

def cancelarreto(uid:int) -> list:
    jugadores = playerhandler.fetchjugadores()
    encontrado = False
    for jugador in jugadores.keys():
        if str(uid) == jugadores[jugador]["discord"]:
            encontrado = True
            if len(list(jugadores[jugador]["reto"].keys())) >=1:
                del jugadores[jugador]["reto"][list(jugadores[jugador]["reto"].keys())[0]]
                embed = discord.Embed(title=f"Cancelaste tu reto :(", color=discord.Color.red())
                playerhandler.setjugadores(jugadores)
                return embed
            else:
                embed = discord.Embed(title=f"No has solicitado ningun reto :(", color=discord.Color.red())
                return embed             
    if encontrado == False:    
        embed = discord.Embed(title=f"Si quieres usar este comando tendras que registrarte con /vincular <link>", color=discord.Color.red())
        return embed