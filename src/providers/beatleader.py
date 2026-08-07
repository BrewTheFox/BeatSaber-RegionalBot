import websockets
from core import player_handler
import json
import aiohttp
import discord
import asyncio
import logging
from database import manager
from core.load_config import get_string, get_configuration
from core.embeds import error_with_fields

COUNTRY = get_configuration()["Country"]


async def get_player_info(did: int) -> tuple:
    session = aiohttp.ClientSession()
    player = manager.load_player_discord(str(did))
    if player:
        async with session as ses:
            async with ses.get(
                f"https://api.beatleader.com/player/{player[0]}?stats=true&keepOriginalId=false"
            ) as request:
                data = json.loads(await request.text())
        embed = player(discord.Color.purple(), data)
        return embed, False
    embed = error_with_fields(
        get_string("AskUserToLink", "Misc"),
        [{"name": get_string("NoLinkedAccountUser", "Misc"), "value": " "}],
    )
    return embed, True


async def get_pass(player_id: str):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(
            f"https://api.beatleader.com/player/{player_id}?keepOriginalId=false"
        ) as request:
            player_info = json.loads(await request.text())

    manager.insert_top_player(
        1, player_id, player_info["pp"]
    )  # Take into account that 1 = BeatLeader
    old_pp = manager.get_player_pp(1, player_id)
    players_passed = list(manager.get_players_between(1, old_pp[0], player_info["pp"]))
    try:
        if player_id == players_passed[-1][0]:
            players_passed.pop(-1)
        if len(players_passed) < 1 or players_passed == None:
            return [False, None, 0, 0, "0"]
        async with aiohttp.ClientSession() as ses:
            async with ses.get(
                f"https://api.beatleader.com/player/{players_passed[-1][0]}?keepOriginalId=false"
            ) as request:
                adversarial_info = json.loads(await request.text())
        manager.update_player_pp(1, player_id, player_info["pp"])
        return [
            True,
            adversarial_info["name"],
            adversarial_info["id"],
            abs(player_info["pp"] - adversarial_info["pp"]),
            str(player_info["countryRank"]),
        ]
    except:
        return [False, None, 0, 0, "0"]


async def receive(client: discord.Client):
    while True:
        try:
            async with websockets.connect(
                "wss://sockets.api.beatleader.xyz/scores"
            ) as socket:
                while True:
                    packet = await socket.recv()
                    if packet and "{" in packet:
                        await player_handler.check_local_player_data(client)
                        data = json.loads(packet)
                        data["Beatleader"] = True
                        asyncio.create_task(
                            player_handler.plays_plus_one(
                                data["playerId"], "Beatleader", client
                            )
                        )
                        if data["country"] == COUNTRY or manager.load_player_id(
                            data["playerId"]
                        ):
                            logging.info(
                                f"Game by {data["player"]["name"]} has been registered!"
                            )
                            player_handler.update_local_player_data(
                                int(data["playerId"]), data
                            )
        except Exception as e:
            logging.error(f"Disconnected from web beatleader's socket. {e}")
