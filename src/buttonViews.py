import discord
import DataBaseManager
from loadconfig import GetString

class Buttons(discord.ui.View):
    def __init__(self):
        super().__init__()

    def AddButton(self, text:str, link:str, emoji:str="<:scoresaber:1326637802963734528>"):
        button = discord.ui.Button(label=text, url=link, style=discord.ButtonStyle.url, emoji=emoji)
        self.add_item(button)

class AcceptButtons(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
    
    def Buttons(self, AcceptText:str, DenyText:str, UserID:str, ChallengedUserID:str, SongID:str):
        accept = discord.ui.Button(label=AcceptText, row=True, custom_id=f"{ChallengedUserID}-{UserID}-{SongID}-accept", style=discord.ButtonStyle.success)
        accept.callback = self.InteractionCallback
        self.add_item(accept)
        deny = discord.ui.Button(label=DenyText, row=True, custom_id=f"{ChallengedUserID}-{UserID}-{SongID}-deny", style=discord.ButtonStyle.red)
        deny.callback = self.InteractionCallback
        self.add_item(deny)
        song = discord.ui.Button(label=GetString("DownloadSong", "ScoreEmbed"), url="https://beatsaver.com/maps/" + SongID, emoji=GetString("BeatSaverEmoji", "ScoreEmbed"), row=True, style=discord.Button.url)
        self.add_item(song)
    
    async def InteractionCallback(self, interaction:discord.Interaction):
        data = interaction.data["custom_id"].split("-")
        if not data[0] == str(interaction.user.id):
            await interaction.response.send_message(embed=discord.Embed(colour=discord.Colour.red(), title=GetString("InvalidPlayer", "Challenges")), ephemeral=True)
            return
        if data[3] == "deny":
            await interaction.message.delete()
            await interaction.response.send_message(content=f"<@{data[0]}> <@{data[1]}>", embed=discord.Embed(colour=discord.Colour.red(), title=GetString("UserChallengeDeny", "Challenges")))
            return
        if data[3] == "accept":
            await interaction.message.delete()
            challengerID = DataBaseManager.LoadPlayerDiscord(data[0])[0]
            challengedID = DataBaseManager.LoadPlayerDiscord(data[1])[0]
            if DataBaseManager.SetChallenge(challengerID, challengedID, data[2]):
                await interaction.response.send_message(content=f"<@{data[0]}> <@{data[1]}>", embed=discord.Embed(colour=discord.Color.green(), title=GetString("UserChallengeAccept", "Challenges").replace("{{SongID}}", data[2])))
                return
            else:
                await interaction.response.send_message(embed=discord.Embed(colour=discord.Colour.red(), title=GetString("UserHasChallenge", "Challenges")))
                return