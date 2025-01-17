import DataBaseManager
import DataBaseConn
import challenges
from loadconfig import GetString, GetConfiguration
from classes import player
from Embeds import PlayerEmbed
from discord import Color

DataBaseManager.database = DataBaseConn.db(":memory:")

def testInsertPlayer():
    playerinstance = player('99999', "444444", None, 0, 0)
    DataBaseManager.InsertPlayer(playerinstance)
    retrievedplayer = DataBaseManager.LoadPlayerDiscord("444444")
    assert retrievedplayer.id == playerinstance.id
    assert retrievedplayer.discord == playerinstance.discord
    assert retrievedplayer.challenge == playerinstance.challenge
    assert retrievedplayer.total_points == playerinstance.total_points
    assert retrievedplayer.points == playerinstance.points

def testPlayerLoading():
    retrievedplayerdiscord = DataBaseManager.LoadPlayerDiscord("444444")
    invalidplayerdiscord = DataBaseManager.LoadPlayerDiscord("inexistent")
    retrievedplayerid = DataBaseManager.LoadPlayerID('99999')
    invalidplayerid = DataBaseManager.LoadPlayerID("inexistent")
    assert type(retrievedplayerdiscord) == player
    assert type(retrievedplayerid) == player
    assert invalidplayerdiscord == False
    assert invalidplayerid == False

def testChallengeGeneration():
    challenge = challenges.GenerateChallenge('444444', "Easy")
    assert challenge.title != GetString("AlreadyChallenged", "Challenges")
    assert challenge.title != GetString("UserHasNoLinkedAccount", "Misc")
    challenge = challenges.GenerateChallenge('99999', "Easy")
    assert challenge.title == GetString("UserHasNoLinkedAccount", "Misc")
    challenge = challenges.GenerateChallenge('444444', "Easy")
    assert challenge.title == GetString("AlreadyChallenged", "Challenges")
    player = DataBaseManager.LoadPlayerID('99999')
    assert player.challenge != None

def testChallengeCompletion():
    DataBaseManager.CompleteChallenge('99999')
    player = DataBaseManager.LoadPlayerID('99999')
    assert player.challenge == None
    assert player.total_points == 500
    assert player.points == None

def testChallengeCancellation():
    embed = challenges.CancelChallenge('444444')
    assert embed.title == GetString("UserHasNoChallenge", "Challenges")
    challenges.GenerateChallenge('444444', "Hard")
    embed = challenges.CancelChallenge('444444')
    assert embed.title == GetString("CancelChallenge", "Challenges")

def testPlayerDeletion():
    DataBaseManager.RemovePlayer('444444')
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