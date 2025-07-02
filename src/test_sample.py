import DataBaseManager as DataBaseManager
import DataBaseConn as DataBaseConn
import challenges as challenges
from loadconfig import GetString, GetConfiguration
from Embeds import PlayerEmbed
from discord import Color

DataBaseManager.database = DataBaseConn.db(":memory:")

def testInsertPlayer():

    DataBaseManager.InsertPlayer("444444", "99999")
    retrievedplayer = DataBaseManager.LoadPlayerDiscord("444444")
    assert "444444" == retrievedplayer[0]
    assert "99999" == retrievedplayer[1]
    assert 0 == retrievedplayer[2]

def testPlayerLoading():
    invalidplayerdiscord = DataBaseManager.LoadPlayerDiscord("inexistent")
    invalidplayerid = DataBaseManager.LoadPlayerID("inexistent")
    assert invalidplayerdiscord == False
    assert invalidplayerid == False

def testPlayerDeletion():
    DataBaseManager.DeletePlayer('444444')
    retrievedplayerdiscord = DataBaseManager.LoadPlayerDiscord("444444")
    assert retrievedplayerdiscord == False

def testPlayerEmbed():
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
        }
    }
    embed = PlayerEmbed(Color.random(), data)
    assert embed.title == GetConfiguration()["Strings"]["ProfileRequest"]["ProfileOf"].replace("{{name}}", data["name"])
    del data["avatar"]
    data["profilePicture"] = "https://example.com/profile_picture.jpg"
    embed = PlayerEmbed(Color.random(), data)
    assert embed.title == GetConfiguration()["Strings"]["ProfileRequest"]["ProfileOf"].replace("{{name}}", data["name"])