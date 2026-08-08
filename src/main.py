import discord
from discord.ext.commands import has_permissions
from dotenv import load_dotenv
import os
from providers import scoresaber, beatleader
from core import challenges, player_handler, embed_poster
import logging
from core.load_config import get_string
from database import manager

logging.basicConfig(filename="../logs.log", encoding="utf-8", level=logging.INFO)

load_dotenv(".././config.env")
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
logging.info("Loading users...")

"""Next lines are just a proxy to other functions"""


@tree.command(
    name=get_string("FetchOwnBl", "Commands"),
    description=get_string("FetchOwnBlDescription", "Commands"),
)
async def fetch_own_bl_data(interaction: discord.Interaction):
    embed, ephemeral = await beatleader.get_player_info(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(
    name=get_string("FetchPersonBl", "Commands"),
    description=get_string("FetchPersonBlDescription", "Commands"),
)
async def fetch_bl_player(interaction: discord.Interaction, miembro: discord.Member):
    embed, ephemeral = await beatleader.get_player_info(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(
    name=get_string("FetchOwnSs", "Commands"),
    description=get_string("FetchOwnSsDescription", "Commands"),
)
async def fetch_own_ss_data(interaction: discord.Interaction):
    embed, ephemeral = await scoresaber.get_player_info(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(
    name=get_string("FetchPersonSs", "Commands"),
    description=get_string("FetchPersonSsDescription", "Commands"),
)
async def fetch_ss_player(interaction: discord.Interaction, miembro: discord.Member):
    embed, ephemeral = await scoresaber.get_player_info(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(
    name=get_string("Unlink", "Commands"),
    description=get_string("UnlinkDescription", "Commands"),
)
async def unlink(interaction: discord.Interaction):
    embed = await player_handler.unlink(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(
    name=get_string("Cancel", "Commands"),
    description=get_string("CancelDescription", "Commands"),
)
async def cancel(interaction: discord.Interaction):
    embed = challenges.cancel_challenge(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(
    name=get_string("GetLeaderboard", "Commands"),
    description=get_string("GetLeaderboardDescription", "Commands"),
)
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.send_message(embed=await challenges.leaderboard(client))


@tree.command(
    name=get_string("ChallengePlayer", "Commands"),
    description=get_string("ChallengePlayerDescription", "Commands"),
)
async def challenge_player(
    interaction: discord.Interaction, bsr: str, jugador: discord.Member
):
    embed = await challenges.challenge_player(bsr, interaction.user, jugador)
    if len(embed) == 3:
        await interaction.response.send_message(
            content=f"<@{jugador.id}>",
            embed=embed[0],
            view=embed[1],
            ephemeral=embed[2],
            delete_after=180,
        )
    else:
        await interaction.response.send_message(embed=embed[0], ephemeral=embed[1])


@tree.command(
    name=get_string("Link", "Commands"),
    description=get_string("LinkDescription", "Commands"),
)
async def link(interaction: discord.Interaction, link: str):
    embed = await player_handler.link(link, interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(
    name=get_string("SetChallengeChannel", "Commands"),
    description=get_string("SetChallengeChannelDescription", "Commands"),
)
@has_permissions(administrator=True)
async def set_challenges_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.create_channel(str(interaction.channel.id), channel_type=0)
        embed = discord.Embed(
            title=get_string("SetChannelSuccess", "Misc"),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=get_string("UserHasNoPerms", "Misc"), color=discord.Color.red()
        )


@tree.command(
    name=get_string("SetScoreChannel", "Commands"),
    description=get_string("SetScoreChannelDescription", "Commands"),
)
@has_permissions(administrator=True)
async def set_score_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.create_channel(str(interaction.channel.id), channel_type=1)
        embed = discord.Embed(
            title=get_string("SetChannelSuccess", "Misc"),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=get_string("UserHasNoPerms", "Misc"), color=discord.Color.red()
        )


@tree.command(
    name=get_string("SetFeedChannel", "Commands"),
    description=get_string("SetFeedChannelDescription", "Commands"),
)
@has_permissions(administrator=True)
async def set_feed_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.create_channel(str(interaction.channel.id), channel_type=2)
        embed = discord.Embed(
            title=get_string("SetChannelSuccess", "Misc"),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=get_string("UserHasNoPerms", "Misc"), color=discord.Color.red()
        )


@tree.command(
    name=get_string("RemoveChannel", "Commands"),
    description=get_string("RemoveChannelDescription", "Commands"),
)
@has_permissions(administrator=True)
async def remove_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.remove_channel(str(interaction.channel.id))
        embed = discord.Embed(
            title=get_string("RemovedChannelSuccess", "Misc"),
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=get_string("UserHasNoPerms", "Misc"), color=discord.Color.red()
        )


@client.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"Synced {str(len(synced))} commands!")
    except Exception as e:
        logging.error(e)

    client.loop.create_task(beatleader.receive(client))
    client.loop.create_task(scoresaber.receive(client))
    client.loop.create_task(embed_poster.update_list())


client.run(os.getenv("token"))
