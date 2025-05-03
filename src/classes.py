import discord

class player():
    def __init__(self, id:str, discord:str, challenge:str | None, total_points:int ,points:int | None):
        self.id = id
        self.discord = discord
        self.challenge = challenge
        self.points = points
        self.total_points = total_points

class Buttons(discord.ui.View):
    def __init__(self):
        super().__init__()

    def AddButton(self, text:str, link:str, emoji:str="<:scoresaber:1326637802963734528>"):
        button = discord.ui.Button(label=text, url=link, style=discord.ButtonStyle.url, emoji=emoji)
        self.add_item(button)