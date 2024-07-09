import discord
from typing import Literal
from dotenv import load_dotenv
import os
import scoresaber
import beatleader
import retos
import playerhandler

load_dotenv("./config.env")
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
print("Cargando usuarios...")


@tree.command(name="ssperfil", description="Obtiene datos de tu perfil de scoresaber")
async def obtenerdatos(interaction: discord.Interaction):
    embed, efimero = scoresaber.getplayerinfo(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="verssperfil", description="Obtiene datos del perfil de scoresaber de alguien del servidor")
async def obtenerjugador(interaction: discord.Interaction, miembro:discord.Member):
    embed, efimero = scoresaber.getplayerinfo(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="desvincular", description="Desvincula y elimina los datos de la cuenta vinculada.")
async def desvincular(interaction: discord.Interaction):
    embed = playerhandler.desvincular(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="cancelar", description="Cancela el reto actual.")
async def cancelar(interaction: discord.Interaction):
    embed = retos.cancelarreto(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="reto", description="Asigna un reto dentro del juego.")
async def retar(interaction: discord.Interaction, dificultad: Literal["Facil", "Dificil", "Expert+"]):
    embed = retos.generarreto(interaction.user.id, dificultad)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="vincular", description="Vincula una cuenta de beatsaber con tu cuenta de discord.")
async def vincular(interaction: discord.Interaction, link:str):
    embed = playerhandler.vincular(link, interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def start_scoresaber_task(client):
    await scoresaber.recibir(client)

async def start_beatleader_task(client):
    await beatleader.recibir(client)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    try:
        synced = await tree.sync()
        print(f"Se sincronizaron {str(len(synced))} comandos")
    except Exception as e:
        print(e)

    client.loop.create_task(start_scoresaber_task(client))
    client.loop.create_task(start_beatleader_task(client))

client.run(os.getenv("token"))
