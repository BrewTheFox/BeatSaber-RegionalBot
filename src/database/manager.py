import connection
from typing import Union, Optional

database = connection.Db()


def get_challenge(id: str):
    return database.get_challenge(id)


def get_challenge_discord(discord: str):
    return database.get_challenge_discord(discord)


def update_challegne(id: str, score: str) -> None:
    return database.update_challenge(id, score)


def leaderboard_top() -> Optional[list]:
    return database.leaderboard_top()


def complete_challenge(id: str):
    return database.complete_challenge(id)


def cancel_challenge(discord: str):
    database.cancel_challenge(discord)


def set_challenge(challenged: str, challenger: str, songID: str) -> bool:
    return database.set_challenge(challenged, challenger, songID)


def load_player_discord(discord: str) -> Union[list, bool]:
    return database.load_player_discord(discord)


def load_player_id(id: int) -> Union[list, bool]:
    return database.load_player_id(id)


def insert_player(discord: str, id: str):
    database.insert_player(discord, id)


def delete_player(discord: str):
    database.delete_player(discord)


def create_channel(channel_id: str, channel_type: int):
    database.create_channel(channel_id, channel_type)


def remove_channel(channel_id: str):
    database.remove_channel(channel_id)


def get_all_channels(channel_type: int) -> list:
    return database.get_all_channels(channel_type)


def get_player_pp(platform: int, id: str) -> Optional[tuple]:
    return database.get_player_pp(platform, id)


def update_player_pp(platform: int, id: str, pp: float) -> None:
    return database.update_player_pp(platform, id, pp)


def insert_top_player(platform: int, id: str, pp: float) -> None:
    database.insert_top_player(platform, id, pp)


def get_players_between(
    platform: int, InitialPP: float, NewPP: float
) -> Optional[list]:
    return database.get_players_between(platform, InitialPP, NewPP)
