import discord
import aiohttp
import asyncio
import re
import logging
from database import manager
import challenges as challenges
from embeds import score, challenge, overcome
from providers import scoresaber
from providers import beatleader

HMDs = {
    "256": "Quest 2",
    "512": "Quest 3",
    "64": "Valve Index",
    "513": "Quest 3S",
    "1": "Rift CV1",
    "2": "Vive",
    "60": "Pico 4",
    "61": "Quest Pro",
    "70": "PS VR2",
    "8": "Windows Mixed Reality",
    "16": "Rift S",
    "65": "Controllable",
    "32": "Quest",
    "4": "Vive Pro",
    "35": "Vive Pro 2",
    "128": "Vive Cosmos",
    "36": "Vive Elite",
    "47": "Vive Focus",
    "38": "Pimax 8K",
    "39": "Pimax 5K",
    "40": "Pimax Artisan",
    "33": "Pico Neo 3",
    "34": "Pico Neo 2",
    "41": "HP Reverb",
    "42": "Samsung WMR",
    "43": "Qiyu Dream",
    "45": "Lenovo Explorer",
    "46": "Acer WMR",
    "66": "Bigscreen Beyond",
    "67": "NOLO Sonic",
    "68": "Hypereal",
    "48": "Arpara",
    "49": "Dell Visor",
    "71": "MeganeX VG1",
    "55": "Huawei VR",
    "56": "Asus WMR",
    "51": "Vive DVT",
    "52": "glasses20",
    "53": "Varjo",
    "69": "Varjo Aero",
    "54": "Vaporeon",
    "57": "Cloud XR",
    "58": "VRidge",
    "50": "e3",
    "59": "Medion Eraser",
    "37": "Miramar",
    "0": "Unknown headset",
    "44": "Disco",
}


async def send_overcome_embed(
    overcame_player: list,
    client: discord.Client,
    player_name: str,
    player_id: str,
    pfp: str,
    platform: str,
):
    if overcame_player[0]:
        overcome_embed, overcome_buttons = overcome(
            overcame_player[1],
            overcame_player[2],
            player_name,
            player_id,
            pfp,
            overcame_player[3],
            overcame_player[4],
            platform,
        )
        for guild in manager.get_all_channels(2):
            try:
                channel = client.get_channel(int(guild[0]))
                await channel.send(embed=overcome_embed, view=overcome_buttons)
            except discord.errors.NotFound or discord.errors.Forbidden:
                manager.remove_channel(guild[0])
            except Exception:
                pass


async def update_list():
    """Syncs the HMDs list with the one in the beatleader github"""
    global HMDs
    session = aiohttp.ClientSession()
    while True:
        logging.info("Updating HMDs")
        logging.info(f"Before: {len(HMDs.keys())}")
        try:
            data_regex = re.compile(
                r"([0-9]*): {\s*name: '(.*)'"
            )  # I wasn't able to find a way to parse the HMDs from beatleader, pos #1 = headset, pos #2 = name
            temp_hmds = {}
            async with session as ses:
                async with ses.get(
                    "https://raw.githubusercontent.com/BeatLeader/beatleader-website/refs/heads/master/src/utils/beatleader/format.js"
                ) as request:
                    data = await request.text()
            headsets = data_regex.finditer(data)
            for headset in headsets:
                temp_hmds[headset[1]] = headset[2]
            HMDs = temp_hmds
        except Exception as e:
            logging.error(e)
        logging.info(f"After: {len(HMDs.keys())}")
        await asyncio.sleep(10000)


async def post_embeds(*, data: dict, client: discord.Client, games_until: int):
    values = [False, 0]
    if "Beatleader" in data.keys():
        player_id = str(data["player"]["id"])
        player_name = data["player"].get("name")
        score_mod = data["contextExtensions"][0]["modifiedScore"]
        pfp = data["player"]["avatar"]
        overcame_player = await beatleader.get_pass(str(player_id))
        await send_overcome_embed(
            overcame_player, client, player_name, player_id, pfp, "Beatleader"
        )
    if "Scoresaber" in data.keys():
        player_id = str(data["commandData"]["score"]["leaderboardPlayerInfo"]["id"])
        player_name = data["commandData"]["score"]["leaderboardPlayerInfo"].get("name")
        score_mod = data["commandData"]["score"]["modifiedScore"]
        overcame_player = await scoresaber.get_pass(str(player_id))
        pfp = data["commandData"]["score"]["leaderboardPlayerInfo"]["profilePicture"]
        await send_overcome_embed(
            overcame_player, client, player_name, player_id, pfp, "Scoresaber"
        )

    challenge = manager.get_challenge(player_id)
    if challenge[0]:  # if the challenge was generated
        embed = await challenges.check_challenge_winner(player_id, score_mod, client)
        if embed:  # if the challenge was completed
            for guild in manager.get_all_channels(
                0
            ):  # Remember that 0 is for challenges, 1 is for scores and 2 for player feedback
                try:
                    channel = client.get_channel(int(guild[0]))
                    await channel.send(embed=embed)
                except Exception as e:
                    print(e)
                    manager.remove_channel(guild[0])

    embed, buttons = await score(data, HMDs, games_until)
    for guild in manager.get_all_channels(
        1
    ):  # Remember that 0 is for challenges, 1 is for scores and 2 for player feedback
        try:
            channel = client.get_channel(int(guild[0]))
            await channel.send(embed=embed, view=buttons)
        except discord.errors.NotFound or discord.errors.Forbidden:
            manager.remove_channel(guild[0])
        except Exception:
            pass
