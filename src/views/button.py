import discord
from database import manager
from core.load_config import get_string


class Buttons(discord.ui.View):
    def __init__(self):
        super().__init__()

    def add_button(
        self, text: str, link: str, emoji: str = "<:scoresaber:1326637802963734528>"
    ):
        button = discord.ui.Button(
            label=text, url=link, style=discord.ButtonStyle.url, emoji=emoji
        )
        self.add_item(button)


class AcceptButtons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    def buttons(
        self,
        accept_text: str,
        deny_text: str,
        user_id: str,
        challenged_user_id: str,
        song_id: str,
    ):
        accept = discord.ui.Button(
            label=accept_text,
            row=True,
            custom_id=f"{challenged_user_id}-{user_id}-{song_id}-accept",
            style=discord.ButtonStyle.success,
        )
        accept.callback = self.interaction_callback
        self.add_item(accept)
        deny = discord.ui.Button(
            label=deny_text,
            row=True,
            custom_id=f"{challenged_user_id}-{user_id}-{song_id}-deny",
            style=discord.ButtonStyle.red,
        )
        deny.callback = self.interaction_callback
        self.add_item(deny)
        song = discord.ui.Button(
            label=get_string("DownloadSong", "ScoreEmbed"),
            url="https://beatsaver.com/maps/" + song_id,
            emoji=get_string("BeatSaverEmoji", "ScoreEmbed"),
            row=True,
            style=discord.Button.url,
        )
        self.add_item(song)

    async def interaction_callback(self, interaction: discord.Interaction):
        data = interaction.data["custom_id"].split("-")
        if not data[0] == str(interaction.user.id):
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=discord.Colour.red(),
                    title=get_string("InvalidPlayer", "Challenges"),
                ),
                ephemeral=True,
            )
            return
        if data[3] == "deny":
            await interaction.message.delete()
            await interaction.response.send_message(
                content=f"<@{data[0]}> <@{data[1]}>",
                embed=discord.Embed(
                    colour=discord.Colour.red(),
                    title=get_string("UserChallengeDeny", "Challenges"),
                ),
            )
            return
        if data[3] == "accept":
            await interaction.message.delete()
            challenger_id = manager.load_player_discord(data[0])[0]
            challenged_id = manager.load_player_discord(data[1])[0]
            if manager.set_challenge(challenger_id, challenged_id, data[2]):
                await interaction.response.send_message(
                    content=f"<@{data[0]}> <@{data[1]}>",
                    embed=discord.Embed(
                        colour=discord.Color.green(),
                        title=get_string("UserChallengeAccept", "Challenges").replace(
                            "{{SongID}}", data[2]
                        ),
                    ),
                )
                return
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=discord.Colour.red(),
                        title=get_string("UserHasChallenge", "Challenges"),
                    )
                )
                return
