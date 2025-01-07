import discord
import random
import DataBaseManager
from Embeds import ErrorEmbed
from loadconfig import GetString, GetConfiguration

def CheckChallenge(id:str, pp:int, estrellas:float, puntaje:int) -> list:
    """Returns a list where the first element is if the challenge was completed and the second one is the score obtanied"""
    challenge, points, _ = DataBaseManager.GetChallenge(id)
    match challenge:
        case("pp"):
            return [pp >= points, pp]
        case("stars"):
            return [estrellas >= points, estrellas]
        case("score"):
            return [puntaje >= points, puntaje]


def GenerateChallenge(uid:int, difficulty:str):
    """This generates a challenge given a difficulty"""
    retos = ["Score", "Stars", "PP"]
    challenge = DataBaseManager.GetChallengeDiscord(str(uid))
    player = DataBaseManager.LoadPlayerDiscord(str(uid))
    if not player:
        embed = ErrorEmbed(GetString("UserHasNoLinkedAccount", "Misc"))
        return embed
    if challenge[0]:
        embed = ErrorEmbed(GetString("AlreadyChallenged", "Challenges"))
        return embed
    kind = random.choice(retos)
    values = GetConfiguration()["ChallengeParams"][difficulty][kind]
    value = random.randint(values[0], values[1])
    if kind == "Score":
        value *= 1000
    DataBaseManager.SetChallenge(str(uid), difficulty, kind.lower(), value)
    embed = discord.Embed(title=GetString(kind+"Challenge", "Challenges").replace("{{var}}", str(value)), color=discord.Colour.from_str(GetConfiguration()["ChallengeParams"][difficulty]["Color"]))
    return embed

def CancelChallenge(uid:int) -> list:
    """Cancels the challenge given by the player"""
    player = DataBaseManager.LoadPlayerDiscord(str(uid))
    challenge = DataBaseManager.GetChallengeDiscord(str(uid))
    if not challenge[0]:
        embed = ErrorEmbed(GetString("UserHasNoChallenge", "Challenges"))
        return embed       
    if not player:
        embed = ErrorEmbed(GetString("UserHasNoLinkedAccount", "Misc"))
        return embed 
    embed = ErrorEmbed(GetString("CancelChallenge", "Challenges"))
    DataBaseManager.CancelChallenge(str(uid))
    return embed