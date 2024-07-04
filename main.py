import discord
from typing import Literal
from dotenv import load_dotenv
import os
import scoresaber
import retos

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

@tree.command(name="desvincular", description="Desvincula y elimina los datos de la cuenta.")
async def desvincular(interaction: discord.Interaction):
    embed = scoresaber.desvincular(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="cancelar", description="Cancela el reto actual.")
async def cancelar(interaction: discord.Interaction):
    embed = retos.cancelarreto(interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="reto", description="Asigna un reto dentro del juego.")
async def retar(interaction: discord.Interaction, dificultad: Literal["Facil", "Dificil", "Expert+"]):
    embed = retos.generarreto(interaction.user.id, dificultad)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="vincularss", description="Vincula una cuenta de scoresaber con tu cuenta de discord.")
async def vincular(interaction: discord.Interaction, link:str):
    embed = scoresaber.vincular(link, interaction.user.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def start_scoresaber_task(client):
    import scoresaber  # Import inside the function to avoid circular import at the module level
    await scoresaber.recibir(client)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    try:
        synced = await tree.sync()
        print(f"Se sincronizaron {str(len(synced))} comandos")
    except Exception as e:
        print(e)

    client.loop.create_task(start_scoresaber_task(client))

client.run(os.getenv("token"))
