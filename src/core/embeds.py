import discord
from load_config import get_string, get_configuration
import logging
from views import button
from providers import beatsaver


def player(color: discord.Colour, data: dict) -> discord.Embed:
    embed = discord.Embed(
        title=get_configuration()["Strings"]["ProfileRequest"]["ProfileOf"].replace(
            "{{name}}", data["name"]
        ),
        color=color,
    )
    embed.set_thumbnail(url=data.get("avatar") or data.get("profilePicture"))
    embed.add_field(name="🌎", value=f"#{data['rank']}", inline=True)
    code_points = [127397 + ord(char) for char in data["country"].upper()]
    embed.add_field(
        name="".join(chr(code) for code in code_points),
        value=f'#{data["countryRank"]}',
        inline=True,
    )
    embed.add_field(
        name=get_string("PerformancePoints"), value=str(data["pp"]), inline=False
    )
    embed.add_field(
        name=get_string("TotalScore"),
        value=str("{:20,.0f}".format(data["scoreStats"]["totalScore"])),
        inline=False,
    )
    embed.add_field(
        name=get_string("TotalPlays"),
        value=str(data["scoreStats"]["totalPlayCount"]),
        inline=False,
    )
    return embed


def error_with_fields(title: str, fields: list):
    embed = discord.Embed(title=title, color=discord.Color.red())
    for field in fields:
        embed.add_field(name=field["name"], value=field["value"])
    return embed


def error(title: str):
    embed = discord.Embed(title=title, color=discord.Color.red())
    return embed


def success(title: str):
    embed = discord.Embed(title=title, color=discord.Color.green())
    return embed


def overcome(
    overcomed_name: str,
    overcomed_id: str,
    overcomer_name: str,
    overcomer_id: str,
    overcomer_pfp: str,
    difference: float,
    leaderboardposition: str,
    platform: str,
):
    buttons = button.Buttons()
    embed = discord.Embed(
        title=get_string("OvercomeTitle", "Overcome")
        .replace("{{name1}}", overcomer_name)
        .replace("{{name2}}", overcomed_name),
        color=discord.Color.blurple(),
    )
    difference_string = f"{int(difference):,}"
    leaderboardposition = f"{int(leaderboardposition):,}"
    embed.add_field(
        name=get_string("OvercomeDescription", "Overcome")
        .replace("{{var1}}", difference_string)
        .replace("{{var2}}", leaderboardposition)
        .replace("{{leaderboard}}", platform),
        value=" ",
    )
    embed.set_thumbnail(url=overcomer_pfp)
    if platform == "Scoresaber":
        buttons.add_button(
            overcomed_name,
            "https://scoresaber.com/u/" + overcomed_id,
            get_string("ScoreSaberEmoji", "ScoreEmbed"),
        )
        buttons.add_button(
            overcomer_name,
            "https://scoresaber.com/u/" + overcomer_id,
            get_string("ScoreSaberEmoji", "ScoreEmbed"),
        )
    else:
        buttons.add_button(
            overcomed_name,
            "https://beatleader.com/u/" + overcomed_id,
            get_string("BeatLeaderEmoji", "ScoreEmbed"),
        )
        buttons.add_button(
            overcomer_name,
            "https://beatleader.com/u/" + overcomer_id,
            get_string("BeatLeaderEmoji", "ScoreEmbed"),
        )
    return embed, buttons


def challenge(data: dict, challenge: str, points: str, values: list):
    if "Scoresaber" in data.keys() and "Beatleader" in data.keys():
        player_name = data["commandData"]["score"]["leaderboardPlayerInfo"].get("name")
        pfp = data["commandData"]["score"]["leaderboardPlayerInfo"]["profilePicture"]
    if "Beatleader" in data.keys() and not "Scoresaber" in data.keys():
        player_name = data["player"].get("name")
        pfp = data["player"]["avatar"]
    if "Scoresaber" in data.keys() and not "Beatleader" in data.keys():
        player_name = data["commandData"]["score"]["leaderboardPlayerInfo"]["name"]
        pfp = data["commandData"]["score"]["leaderboardPlayerInfo"]["profilePicture"]

    embed = discord.Embed(
        title=get_string("UserCompletedChallenge", "Challenges").replace(
            "{{name}}", player_name
        )
    )
    embed.add_field(
        name=get_string("Category", "Challenges"), value=challenge.title(), inline=False
    )
    embed.add_field(
        name=get_string("OvercomeValue", "Challenges"), value=points, inline=False
    )
    embed.add_field(
        name=get_string("ObtainedValue", "Challenges"), value=values[1], inline=False
    )
    embed.set_thumbnail(url=pfp)
    return embed


async def score(data: dict, HMDs: dict, games_until: int):
    buttons = button.Buttons()
    if "Scoresaber" in data.keys() and "Beatleader" in data.keys():
        try:
            provider = get_string("BothPlatforms", "ScoreEmbed")
            color = discord.Color.dark_orange()
            player_name = data["commandData"]["score"]["leaderboardPlayerInfo"].get(
                "name"
            )
            logging.debug(
                f"Variables multiples asignadas para el usuario {player_name}"
            )
            player_id = str(data["commandData"]["score"]["leaderboardPlayerInfo"]["id"])
            pfp = data["commandData"]["score"]["leaderboardPlayerInfo"][
                "profilePicture"
            ]
            song_name = data["commandData"]["leaderboard"]["songName"]
            cover_image = data["commandData"]["leaderboard"]["coverImage"]
            mod_score = data["commandData"]["score"]["modifiedScore"]
            base_score = data["commandData"]["score"]["baseScore"]
            hmd = HMDs[str(data["hmd"])]
            pp = data["commandData"]["score"]["pp"], data["pp"]
            stars = round(
                max(
                    [
                        data["commandData"]["leaderboard"]["stars"],
                        data["leaderboard"]["difficulty"]["stars"] or 0,
                    ]
                ),
                2,
            )
            weight = (
                data["commandData"]["score"]["weight"],
                data["contextExtensions"][0]["weight"],
            )
            max_score = data["commandData"]["leaderboard"]["maxScore"]
            song_hash = data["commandData"]["leaderboard"].get("songHash")
            difficulty = data["commandData"]["leaderboard"]["difficulty"][
                "difficultyRaw"
            ]
            fails = int(data["commandData"]["score"]["badCuts"]) + int(
                data["commandData"]["score"]["missedNotes"]
            )
            beatleader_replay = "https://replay.beatleader.com/?scoreId=" + str(
                data["id"]
            )
            buttons.add_button(
                f"{player_name} Beatleader",
                f"https://beatleader.com/u/{player_id}",
                get_string("BeatLeaderEmoji", "ScoreEmbed"),
            )
            buttons.add_button(
                f"{player_name} Scoresaber",
                f"https://scoresaber.com/u/{player_id}",
                get_string("ScoreSaberEmoji", "ScoreEmbed"),
            )
            song = await beatsaver.song_info(song_hash, difficulty)
        except Exception as e:
            logging.error(f"{e} while fetching vars for {player_name} (both providers)")
    if "Beatleader" in data.keys() and not "Scoresaber" in data.keys():
        try:
            provider = "Beatleader"
            color = discord.Color.dark_purple()
            player_name = data["player"].get("name")
            logging.debug(
                f"Variables Beatleader asignadas para el usuario {player_name}"
            )
            player_id = str(data["player"]["id"])
            hmd = HMDs[str(data["hmd"])]
            pfp = data["player"]["avatar"]
            song_hash = data["leaderboard"]["song"].get("hash")
            difficulty = data["leaderboard"]["difficulty"]["difficultyName"]
            mode_name = data["leaderboard"]["difficulty"]["modeName"]
            song_name = data["leaderboard"]["song"]["name"]
            cover_image = data["leaderboard"]["song"]["coverImage"]
            mod_score = data["modifiedScore"]
            base_score = data["baseScore"]
            pp = data["pp"]
            weight = data["weight"]
            stars = round(data["leaderboard"]["difficulty"]["stars"] or 0, 2)
            max_score = data["leaderboard"]["difficulty"]["maxScore"]
            fails = abs(data["badCuts"]) + abs(data["missedNotes"])
            replay = "https://replay.beatleader.com/?scoreId=" + str(data["id"])
            song = await beatsaver.song_info(song_hash, f"_{difficulty}_{mode_name}")
            buttons.add_button(
                player_name,
                f"https://beatleader.com/u/{player_id}",
                get_string("BeatLeaderEmoji", "ScoreEmbed"),
            )
        except Exception as e:
            logging.error(f"{e} while fetching vars for {player_name} (beatleader)")
    if "Scoresaber" in data.keys() and not "Beatleader" in data.keys():
        try:
            provider = "ScoreSaber"
            color = discord.Color.gold()
            player_name = data["commandData"]["score"]["leaderboardPlayerInfo"]["name"]
            logging.debug(f"Assigned scoresaber vars for {player_name}")
            player_id = str(data["commandData"]["score"]["leaderboardPlayerInfo"]["id"])
            pfp = data["commandData"]["score"]["leaderboardPlayerInfo"][
                "profilePicture"
            ]
            hmd = data["commandData"]["score"]["deviceHmd"]
            song_name = data["commandData"]["leaderboard"]["songName"]
            cover_image = data["commandData"]["leaderboard"]["coverImage"]
            mod_score = data["commandData"]["score"]["modifiedScore"]
            base_score = data["commandData"]["score"]["baseScore"]
            pp = data["commandData"]["score"]["pp"]
            weight = data["commandData"]["score"]["weight"]
            stars = data["commandData"]["leaderboard"]["stars"]
            max_score = data["commandData"]["leaderboard"]["maxScore"]
            song_hash = data["commandData"]["leaderboard"]["songHash"]
            difficulty = data["commandData"]["leaderboard"]["difficulty"][
                "difficultyRaw"
            ]
            fails = int(data["commandData"]["score"]["badCuts"]) + int(
                data["commandData"]["score"]["missedNotes"]
            )
            song = await beatsaver.song_info(song_hash, difficulty)
            buttons.add_button(
                player_name,
                f"https://scoresaber.com/u/{player_id}",
                get_string("ScoreSaberEmoji", "ScoreEmbed"),
            )
        except Exception as e:
            logging.error(f"{e} while fetching vars for {player_name} (scoresaber)")
    difficulty = (song["difficulty"]).replace("Plus", "+")
    data_keys = data.keys()
    embed = discord.Embed(
        title=get_string("EmbedTitle", "ScoreEmbed").replace("{{name}}", player_name),
        color=color,
    )
    embed.add_field(
        name=get_string("ToPass", "ScoreEmbed")
        .replace("{{song}}", song_name)
        .replace("{{difficulty}}", difficulty),
        value=" ",
        inline=False,
    )
    embed.set_thumbnail(url=pfp)
    embed.set_image(url=cover_image)
    embed.add_field(
        name=get_string("Score", "ScoreEmbed"),
        value="{:20,.0f}".format(mod_score),
        inline=True,
    )

    if provider == "ScoreSaber" or provider == "Beatleader":
        embed.add_field(
            name=get_string("AddedPerformancePoints", "ScoreEmbed"),
            value=str(round(float(pp * weight), 2)),
            inline=True,
        )
    else:
        embed.add_field(
            name=get_string("AddedPerformancePointsBeatLeader", "ScoreEmbed"),
            value=str(round(float(pp[1] * weight[1]), 2)),
            inline=True,
        )
        embed.add_field(
            name=get_string("AddedPerformancePointsScoreSaber", "ScoreEmbed"),
            value=str(round(float(pp[0] * weight[0]), 2)),
            inline=True,
        )

    if max_score != 0:
        embed.add_field(
            name=get_string("Average", "ScoreEmbed"),
            value=str(round((base_score / max_score) * 100, 2)) + "%",
            inline=True,
        )
        embed.add_field(
            name=get_string("Stars", "ScoreEmbed"),
            value=str(stars) + "★",
            inline=True,
        )

        if not "error" in song.keys():
            embed.add_field(
                name=get_string("GoodvsWrong", "ScoreEmbed"),
                value=str(song["notes"] - fails) + "/" + str(song["notes"]),
                inline=True,
            )
        if "Scoresaber" in data_keys:
            hmd += f'({data["commandData"]["score"]["deviceControllerRight"]})'

        embed.add_field(name=get_string("Device", "ScoreEmbed"), value=hmd, inline=True)
        embed.add_field(
            name=get_string("Platform", "ScoreEmbed"), value=provider, inline=True
        )

        if "replay" in data_keys:
            buttons.add_button(
                get_string("ViewReplay", "ScoreEmbed"),
                replay,
                "<a:bspepe:1368253102880329808>",
            )

        if not "error" in song.keys():
            buttons.add_button(
                get_string("DownloadSong", "ScoreEmbed"),
                f"https://beatsaver.com/maps/{song['id']}",
                get_string("BeatSaverEmoji", "ScoreEmbed"),
            )
        embed.set_footer(
            text=get_string("LastGameBefore", "ScoreEmbed").replace(
                "{{var}}", str(games_until)
            )
        )
    return embed, buttons
