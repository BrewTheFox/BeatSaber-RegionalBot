import discord
from loadconfig import GetString, GetConfiguration

def PlayerEmbed(color:discord.Colour, data:dict) -> discord.Embed:
    embed = discord.Embed(title=GetConfiguration["strings"]["ProfileRequest"]["ProfileOf"].replace("{{name}}", data["name"]), color=color)
    embed.set_thumbnail(url=data['avatar'])
    embed.add_field(name="🌎", value=f"#{data['rank']}", inline=True)
    code_points = [127397 + ord(char) for char in data['country'].upper()]
    embed.add_field(name=''.join(chr(code) for code in code_points), value=f'#{data["countryRank"]}', inline=True)
    embed.add_field(name=GetString("PerformancePoints"), value=str(data["pp"]), inline=False)
    embed.add_field(name=GetString("TotalScore"), value=str('{:20,.0f}'.format(data["scoreStats"]["totalScore"])), inline=False)
    embed.add_field(name=GetString("TotalPlays"), value=str(data["scoreStats"]["totalPlayCount"]), inline=False)
    return embed

def ErrorWithFieldsEmbed(title:str, fields:list):
    embed = discord.Embed(title=title, color=discord.Color.red())
    for field in fields:
        embed.add_field(name=field["name"], value=field["value"])
    return embed

def ErrorEmbed(title:str):
    embed = discord.Embed(title=title, color=discord.Color.red())
    return embed

def SuccessEmbed(title:str):
    embed = discord.Embed(title=title, color=discord.Color.green())
    return embed   