import discord
from discord.ext.commands import has_permissions
from dotenv import load_dotenv
import os
from providers import scoresaber, beatleader
from core import challenges, player_handler, embed_poster
import logging
from database import manager

logging.basicConfig(filename="../logs.log", encoding="utf-8", level=logging.INFO)

load_dotenv(".././config.env")
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
logging.info("Loading users...")

"""Las lineas de abajo se encargan de hacer de Proxy para la comunicacion entre discord y las funciones"""


@tree.command(name="blperfil", description="Obtiene datos de tu perfil de Beatleader")
async def fetch_own_bl_data(interaction: discord.Interaction):
    embed, ephemeral = await beatleader.get_player_info(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(
    name="verblperfil",
    description="Obtiene datos del perfil de Beatleader de alguien del servidor",
)
async def fetch_bl_player(interaction: discord.Interaction, miembro: discord.Member):
    embed, ephemeral = await beatleader.get_player_info(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(name="ssperfil", description="Obtiene datos de tu perfil de scoresaber")
async def fetch_own_ss_data(interaction: discord.Interaction):
    embed, ephemeral = await scoresaber.get_player_info(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(
    name="verssperfil",
    description="Obtiene datos del perfil de scoresaber de alguien del servidor",
)
async def fetch_ss_player(interaction: discord.Interaction, miembro: discord.Member):
    embed, ephemeral = await scoresaber.get_player_info(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@tree.command(
    name="desvincular",
    description="Desvincula y elimina los datos de la cuenta vinculada.",
)
async def unlink(interaction: discord.Interaction):
    embed = await player_handler.unlink(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="cancelar", description="Cancela el reto actual.")
async def cancel(interaction: discord.Interaction):
    embed = challenges.cancel_challenge(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="leaderboard", description="Retorna el leaderboard de los retos :)")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.send_message(embed=await challenges.Leaderboard(client))


@tree.command(name="reto", description="Te permite retar a un jugador en una cancion.")
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
    name="vincular",
    description="Vincula una cuenta de beatsaber con tu cuenta de discord.",
)
async def link(interaction: discord.Interaction, link: str):
    embed = await player_handler.link(link, interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(
    name="establecer_canal_retos",
    description="Establece el canal de retos en el servidor.",
)
@has_permissions(administrator=True)
async def set_challenges_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.create_channel(str(interaction.channel.id), channel_type=0)
        embed = discord.Embed(
            title="El canal se ha establecido exitosamente para los retos :)",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="No tienes permiso para esto", color=discord.Color.red()
        )


@tree.command(
    name="establecer_canal_scores",
    description="Establece el canal de scores en el servidor.",
)
@has_permissions(administrator=True)
async def set_score_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.create_channel(str(interaction.channel.id), channel_type=1)
        embed = discord.Embed(
            title="El canal se ha establecido exitosamente para los scores :)",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="No tienes permiso para esto", color=discord.Color.red()
        )


@tree.command(
    name="establecer_canal_feed",
    description="Establece el canal del feed de jugadores en el servidor.",
)
@has_permissions(administrator=True)
async def set_feed_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.create_channel(str(interaction.channel.id), channel_type=2)
        embed = discord.Embed(
            title="El canal se ha establecido exitosamente para el feed de los jugadores :)",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="No tienes permiso para esto", color=discord.Color.red()
        )


@tree.command(name="eliminar_canal", description="Bye Bye SPAM")
@has_permissions(administrator=True)
async def remove_channel(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator == True:
        manager.remove_channel(str(interaction.channel.id))
        embed = discord.Embed(
            title="El canal se ha eliminado satisfactoriamente",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="No tienes permiso para esto", color=discord.Color.red()
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
