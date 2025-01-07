import discord
import random
import DataBaseManager


def checkchallenge(id:str, pp:int, estrellas:float, puntaje:int) -> list:
    """Valida que el reto se haya cumplido"""

    challenge, points, _ = DataBaseManager.GetChallenge(id)
    if challenge == "pp":
        return [pp >= points, pp]
    if challenge == "stars":
        return [estrellas >= points, estrellas]
    if challenge == "score":
        return [puntaje >= points, puntaje]

def generatechallenge(uid:int, dificultad:str):
    """Solamente genera un reto en base al id del jugador y la dificultad solicitada"""
    retos = ["score", "stars", "pp"]
    challenge = DataBaseManager.GetChallengeDiscord(str(uid))
    player = DataBaseManager.LoadPlayerDiscord(str(uid))
    if not player:
        embed = discord.Embed(title="Porfavor vincula tu cuenta con /vincular <link> para acceder a esta funcion.", color=discord.Color.red())
        return embed
    if challenge:
        embed = discord.Embed(title=f"¡Ya solicitaste un reto /cancelar si no lo quieres!", color=discord.Color.red())
        return embed
    
    kind = random.choice(retos)
    if dificultad == "Facil":
        if kind == "score":
            score = random.randint(150, 600) * 1000
            DataBaseManager.SetChallenge(str(uid), "Easy", "score", score)
            embed = discord.Embed(title=f"¡Consigue mas de {score} puntos en un nivel!", color=discord.Color.blue())
        if kind == "stars":
            stars = random.randint(1,5)
            DataBaseManager.SetChallenge(str(uid), "Easy", "stars", stars)
            embed = discord.Embed(title=f"¡Pasate un nivel de {stars} estrellas o mas!", color=discord.Color.blue())
        if kind == "pp":
            quantity = random.randint(10,100)
            DataBaseManager.SetChallenge(str(uid), "Easy", "pp", quantity)
            embed = discord.Embed(title=f"¡Pasate un nivel con mas de {quantity} PP!", color=discord.Color.blue())
        return embed
    
    if dificultad == "Dificil":
        if kind == "score":
            score = random.randint(600, 1200) * 1000
            DataBaseManager.SetChallenge(str(uid), "Hard", "score", score)
            embed = discord.Embed(title=f"¡Consigue mas de {score} puntos en un nivel!", color=discord.Color.green())
        if kind == "stars":
            stars = random.randint(5,9)
            DataBaseManager.SetChallenge(str(uid), "Hard", "stars", stars)
            embed = discord.Embed(title=f"¡Pasate un nivel de {stars} estrellas o mas!", color=discord.Color.green())
        if kind == "pp":
            quantity = random.randint(100,250)
            DataBaseManager.SetChallenge(str(uid), "Hard", "pp", quantity)
            embed = discord.Embed(title=f"¡Pasate un nivel con mas de {quantity} PP!", color=discord.Color.green())
        return embed
        
    if dificultad == "Expert+":
        if kind == "score":
            score = random.randint(1200, 2000) * 1000
            DataBaseManager.SetChallenge(str(uid), "Expert+", "score", score)
            embed = discord.Embed(title=f"¡Consigue mas de {score} puntos en un nivel!", color=discord.Color.orange())
        if kind == "stars":
            stars = random.randint(10,13)
            DataBaseManager.SetChallenge(str(uid), "Expert+", "stars", stars)
            embed = discord.Embed(title=f"¡Pasate un nivel de {stars} estrellas o mas!", color=discord.Color.orange())
        if kind == "pp":
            quantity = random.randint(400,550)
            DataBaseManager.SetChallenge(str(uid), "Expert+", "pp", quantity)
            embed = discord.Embed(title=f"¡Pasate un nivel con mas de {quantity} PP!", color=discord.Color.orange())
        return embed

def cancelchallenge(uid:int) -> list:
    """Cancela el reto solicitado por el jugador"""
    player = DataBaseManager.LoadPlayerDiscord(str(uid))
    challenge, _, _ = DataBaseManager.GetChallengeDiscord(str(uid))
    if not player:
        embed = discord.Embed(title=f"Si quieres usar este comando tendras que registrarte con /vincular <link>", color=discord.Color.red())
        return embed
    if not challenge:
        embed = discord.Embed(title=f"No has solicitado ningun reto :(", color=discord.Color.red())
        return embed        
    embed = discord.Embed(title=f"Cancelaste tu reto :(", color=discord.Color.red())
    DataBaseManager.CancelChallenge()
    return embed