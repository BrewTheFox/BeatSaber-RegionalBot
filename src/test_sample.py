from database import manager
from database import connection
from core.load_config import get_string, get_configuration
from core.embeds import player
from discord import Color

manager.database = connection.Db(":memory:")

def test_insert_player():

    manager.insert_player("444444", "99999")
    retrieved_player = manager.load_player_discord("444444")
    assert "444444" == retrieved_player[1]
    assert "99999" == retrieved_player[0]
    assert 0 == retrieved_player[2]


def test_player_loading():
    invalid_player_discord = manager.load_player_discord("inexistent")
    invalid_player_id = manager.load_player_id("inexistent")
    assert invalid_player_discord == False
    assert invalid_player_id == False


def test_player_deletion():
    manager.delete_player("444444")
    retrieved_player_discord = manager.load_player_discord("444444")
    assert retrieved_player_discord == False


def test_player_embed():
    data = {
        "name": "BrewTheFox",
        "avatar": "https://example.com/avatar.jpg",
        "rank": 12345,
        "country": "CO",
        "countryRank": 42,
        "pp": 5000.5,
        "scoreStats": {
            "totalScore": 1234567890,
            "totalPlayCount": 876,
        },
    }
    embed = player(Color.random(), data)
    assert embed.title == get_configuration()["Strings"]["ProfileRequest"][
        "ProfileOf"
    ].replace("{{name}}", data["name"])
    del data["avatar"]
    data["profilePicture"] = "https://example.com/profile_picture.jpg"
    embed = player(Color.random(), data)
    assert embed.title == get_configuration()["Strings"]["ProfileRequest"][
        "ProfileOf"
    ].replace("{{name}}", data["name"])
