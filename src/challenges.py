import discord
import DataBaseManager as DataBaseManager
import re
import beatsaver
import buttonViews
from typing import Optional
from Embeds import ErrorEmbed
from loadconfig import GetString

BSRRE = re.compile(r"!bsr ([a-z-0-9]*)")

async def ChallengePlayer(bsr:str, challenger:discord.Member, player:discord.Member):
    """Lets you challenge a player to get a better score than you on a song."""
    code = BSRRE.findall(bsr)
    if len(code) < 1:
        return [ErrorEmbed(GetString("InvalidBSR", "Challenges")), True]
    code = code[-1]
    songinfo = await beatsaver.songexists(code)
    if not songinfo[0]:
        return [ErrorEmbed(GetString("InvalidBSR", "Challenges")), True]
    if not DataBaseManager.LoadPlayerDiscord(challenger.id):
        return [ErrorEmbed(GetString("NoLinkedAccountUser", "Misc")), True]
    if not DataBaseManager.LoadPlayerDiscord(player.id):
        return [ErrorEmbed(GetString("AskUserToLink", "Misc")), True]
    if player.id == challenger.id:
        return [ErrorEmbed(GetString("InvalidUser", "Challenges")), True]
    buttons = buttonViews.AcceptButtons()
    buttons.Buttons("Aceptar", "Cancelar", challenger.id, player.id, code)
    embed = discord.Embed(title=GetString("UserChallengedNotification", "Challenges").replace("{{challenger}}", challenger.display_name).replace("{{challenged}}", player.display_name).replace("{{songName}}", songinfo[1]), color=discord.Colour.og_blurple())
    embed.set_image(url=songinfo[2])
    return [embed, buttons, False]

async def Leaderboard(client:discord.Client) -> discord.Embed:
    tops = DataBaseManager.LeaderboardTop()
    if len(tops) == 0:
        return discord.Embed(title=GetString("Leaderboard", "Challenges"), description="```Nadie ha jugado...```", color=discord.Color.yellow())
    text = "```"
    for index, top in enumerate(tops):
        text += f"{index + 1}. {(await client.fetch_user(top[0])).display_name} - {top[1]} pts\n"
    text += "```"
    return discord.Embed(title=GetString("Leaderboard", "Challenges"), description=text, color=discord.Color.yellow())

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

async def CheckChallengeWinner(playerID:str, score:int, client:discord.Client) -> Optional[discord.Embed]:
    """Checks the winner of the challenge if it is ready to be considered as completed!"""
    challenge = DataBaseManager.GetChallenge(playerID)
    if challenge[3] == None:
        DataBaseManager.UpdateChallenge(playerID, score)
        return
    if challenge[3] == playerID:
        return
    if challenge[2] > score:
        winner = (await client.fetch_user(DataBaseManager.LoadPlayerID(challenge[3])[1]))
        loser = (await client.fetch_user(DataBaseManager.LoadPlayerID(playerID)[1])).display_name
        message = GetString("UserWonChallenge", "Challenges").replace("{{name1}}", winner.display_name).replace("{{name2}}", loser).replace("{{SongID}}", challenge[1])
        DataBaseManager.CompleteChallenge(winner)
    if challenge[2] < score:
        loser = (await client.fetch_user(DataBaseManager.LoadPlayerID(challenge[3])[1])).display_name
        winner = (await client.fetch_user(DataBaseManager.LoadPlayerID(playerID)[1]))
        message = GetString("UserWonChallenge", "Challenges").replace("{{name1}}", winner.display_name).replace("{{name2}}", loser).replace("{{SongID}}", challenge[1])
        DataBaseManager.CompleteChallenge(winner)     
    embed = discord.Embed(title=message, color=discord.Colour.green())
    embed.thumbnail = winner.display_avatar.url
    return embed