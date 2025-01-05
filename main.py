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

"""Las lineas de abajo se encargan de hacer de Proxy para la comunicacion entre discord y las funciones"""

@tree.command(name="blperfil", description="Obtiene datos de tu perfil de Beatleader")
async def fetchdata(interaction: discord.Interaction):
    embed, efimero = beatleader.getplayerinfo(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="verblperfil", description="Obtiene datos del perfil de Beatleader de alguien del servidor")
async def fetchplayer(interaction: discord.Interaction, miembro:discord.Member):
    embed, efimero = beatleader.getplayerinfo(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="ssperfil", description="Obtiene datos de tu perfil de scoresaber")
async def fetchdata(interaction: discord.Interaction):
    embed, efimero = scoresaber.getplayerinfo(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="verssperfil", description="Obtiene datos del perfil de scoresaber de alguien del servidor")
async def fetchplayer(interaction: discord.Interaction, miembro:discord.Member):
    embed, efimero = scoresaber.getplayerinfo(miembro.id)
    await interaction.response.send_message(embed=embed, ephemeral=efimero)

@tree.command(name="desvincular", description="Desvincula y elimina los datos de la cuenta vinculada.")
async def unlink(interaction: discord.Interaction):
    embed = playerhandler.unlink(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="cancelar", description="Cancela el reto actual.")
async def cancel(interaction: discord.Interaction):
    embed = retos.cancelchallenge(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="reto", description="Asigna un reto dentro del juego.")
async def generatechallenge(interaction: discord.Interaction, dificultad: Literal["Facil", "Dificil", "Expert+"]):
    embed = retos.generatechallenge(interaction.user.id, dificultad)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="vincular", description="Vincula una cuenta de beatsaber con tu cuenta de discord.")
async def link(interaction: discord.Interaction, link:str):
    embed = playerhandler.link(link, interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    try:
        synced = await tree.sync()
        print(f"Se sincronizaron {str(len(synced))} comandos")
    except Exception as e:
        print(e)

    client.loop.create_task(beatleader.recieve(client))
    client.loop.create_task(scoresaber.recieve(client))

client.run(os.getenv("token"))
