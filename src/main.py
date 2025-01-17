import discord
from discord.ext.commands import has_permissions
from typing import Literal
from dotenv import load_dotenv
import os
import scoresaber as scoresaber
import beatleader as beatleader
import challenges as challenges
import playerhandler as playerhandler
import EmbedPoster as EmbedPoster
import logging
import DataBaseManager as DataBaseManager

logging.basicConfig(filename='../logs.log', encoding='utf-8', level=logging.INFO)

load_dotenv(".././config.env")
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
logging.info("Cargando usuarios...")

"""Las lineas de abajo se encargan de hacer de Proxy para la comunicacion entre discord y las funciones"""

@tree.command(name="blperfil", description="Obtiene datos de tu perfil de Beatleader")
async def fetchdata(interaction: discord.Interaction):
    embed, efimero = await beatleader.GetPlayerInfo(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="verblperfil", description="Obtiene datos del perfil de Beatleader de alguien del servidor")
async def fetchplayer(interaction: discord.Interaction, miembro:discord.Member):
    embed, efimero = await beatleader.GetPlayerInfo(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="ssperfil", description="Obtiene datos de tu perfil de scoresaber")
async def fetchdata(interaction: discord.Interaction):
    embed, efimero = await scoresaber.GetPlayerInfo(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="verssperfil", description="Obtiene datos del perfil de scoresaber de alguien del servidor")
async def fetchplayer(interaction: discord.Interaction, miembro:discord.Member):
    embed, efimero = await scoresaber.GetPlayerInfo(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="desvincular", description="Desvincula y elimina los datos de la cuenta vinculada.")
async def unlink(interaction: discord.Interaction):
    embed = await playerhandler.Unlink(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="cancelar", description="Cancela el reto actual.")
async def cancel(interaction: discord.Interaction):
    embed = challenges.CancelChallenge(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="reto", description="Asigna un reto dentro del juego.")
async def generatechallenge(interaction: discord.Interaction, dificultad: Literal["Easy", "Hard", "Expert+"]):
    embed = challenges.GenerateChallenge(interaction.user.id, dificultad)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="vincular", description="Vincula una cuenta de beatsaber con tu cuenta de discord.")
async def link(interaction: discord.Interaction, link:str):
    embed = await playerhandler.Link(link, interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="establecer_canal_retos", description="Establece el canal de retos en el servidor.")
@has_permissions(administrator=True)
async def setChallengeChannel(interaction: discord.Interaction):
    DataBaseManager.SetChannel(str(interaction.channel.id), channel_type=0)
    embed = discord.Embed(title="El canal se ha establecido exitosamente para los retos :)", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="establecer_canal_scores", description="Establece el canal de scores en el servidor.")
@has_permissions(administrator=True)
async def setChallengeChannel(interaction: discord.Interaction):
    DataBaseManager.SetChannel(str(interaction.channel.id), channel_type=1)
    embed = discord.Embed(title="El canal se ha establecido exitosamente para los scores :)", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="establecer_canal_feed", description="Establece el canal del feed de jugadores en el servidor.")
@has_permissions(administrator=True)
async def setChallengeChannel(interaction: discord.Interaction):
    DataBaseManager.SetChannel(str(interaction.channel.id), channel_type=2)
    embed = discord.Embed(title="El canal se ha establecido exitosamente para el feed de los jugadores :)", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="eliminar_canal", description="Bye Bye SPAM")
@has_permissions(administrator=True)
async def setChallengeChannel(interaction: discord.Interaction):
    DataBaseManager.RemoveChannel(str(interaction.channel.id))
    embed = discord.Embed(title="El canal se ha eliminado satisfactoriamente", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"Se sincronizaron {str(len(synced))} comandos")
    except Exception as e:
        logging.error(e)

    client.loop.create_task(beatleader.Recieve(client))
    client.loop.create_task(scoresaber.Recieve(client))
    client.loop.create_task(EmbedPoster.UpdateList())
client.run(os.getenv("token"))
