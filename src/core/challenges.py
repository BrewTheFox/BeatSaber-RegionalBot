import discord
from database import manager
import re
import providers.beatsaver as beatsaver
from views import button
from typing import Optional
from embeds import error
from load_config import get_string

BSRRE = re.compile(r"!bsr ([a-z-0-9]*)")


async def challenge_player(
    bsr: str, challenger: discord.Member, player: discord.Member
):
    """Lets you challenge a player to get a better score than you on a song."""
    code = BSRRE.findall(bsr)
    if len(code) < 1:
        return [error(get_string("InvalidBSR", "Challenges")), True]
    code = code[-1]
    songinfo = await beatsaver.songexists(code)
    if not songinfo[0]:
        return [error(get_string("InvalidBSR", "Challenges")), True]
    if not manager.load_player_discord(challenger.id):
        return [error(get_string("NoLinkedAccountUser", "Misc")), True]
    if not manager.load_player_discord(player.id):
        return [error(get_string("AskUserToLink", "Misc")), True]
    if player.id == challenger.id:
        return [error(get_string("InvalidUser", "Challenges")), True]
    if player.bot:
        return [error(get_string("InvalidUser", "Challenges")), True]
    buttons = button.AcceptButtons()
    buttons.buttons(
        get_string("Accept", "Challenges"),
        get_string("Deny", "Challenges"),
        challenger.id,
        player.id,
        code,
    )
    embed = discord.Embed(
        title=get_string("UserChallengedNotification", "Challenges")
        .replace("{{challenger}}", challenger.display_name)
        .replace("{{challenged}}", player.display_name)
        .replace("{{songName}}", songinfo[1]),
        color=discord.Colour.og_blurple(),
    )
    embed.set_image(url=songinfo[2])
    return [embed, buttons, False]


async def leaderboard(client: discord.Client) -> discord.Embed:
    tops = manager.leaderboard_top()
    if len(tops) == 0:
        return discord.Embed(
            title=get_string("Leaderboard", "Challenges"),
            description=f"```{get_string("NoPlays", "Challenges")}```",
            color=discord.Color.yellow(),
        )
    text = "```"
    for index, top in enumerate(tops):
        text += f"{index + 1}. {(await client.fetch_user(top[0])).display_name} - {top[1]} pts\n"
    text += "```"
    return discord.Embed(
        title=get_string("Leaderboard", "Challenges"),
        description=text,
        color=discord.Color.yellow(),
    )


def cancel_challenge(uid: int) -> list:
    """Cancels the challenge given by the player"""
    player = manager.load_player_discord(str(uid))
    challenge = manager.get_challenge_discord(str(uid))
    if not challenge[0]:
        embed = error(get_string("UserHasNoChallenge", "Challenges"))
        return embed
    if not player:
        embed = error(get_string("UserHasNoLinkedAccount", "Misc"))
        return embed
    embed = error(get_string("CancelChallenge", "Challenges"))
    manager.cancel_challenge(str(uid))
    return embed


async def check_challenge_winner(
    playerID: str, score: int, client: discord.Client
) -> Optional[discord.Embed]:
    """Checks the winner of the challenge if it is ready to be considered as completed!"""
    challenge = manager.get_challenge(playerID)
    if challenge[3] == None:
        manager.update_challegne(playerID, score)
        return
    if challenge[3] == playerID:
        return
    if challenge[2] > score:
        winner = await client.fetch_user(manager.load_player_id(challenge[3])[1])
        loser = (
            await client.fetch_user(manager.load_player_id(playerID)[1])
        ).display_name
        message = (
            get_string("UserWonChallenge", "Challenges")
            .replace("{{name1}}", winner.display_name)
            .replace("{{name2}}", loser)
            .replace("{{SongID}}", challenge[1])
        )
        manager.complete_challenge(winner)
    if challenge[2] < score:
        loser = (
            await client.fetch_user(manager.load_player_id(challenge[3])[1])
        ).display_name
        winner = await client.fetch_user(manager.load_player_id(playerID)[1])
        message = (
            get_string("UserWonChallenge", "Challenges")
            .replace("{{name1}}", winner.display_name)
            .replace("{{name2}}", loser)
            .replace("{{SongID}}", challenge[1])
        )
        manager.complete_challenge(winner)
    embed = discord.Embed(title=message, color=discord.Colour.green())
    embed.thumbnail = winner.display_avatar.url
    return embed
