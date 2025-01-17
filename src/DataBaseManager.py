import DataBaseConn as DataBaseConn
import classes as classes
from typing import Union

database = DataBaseConn.db()

def GetChallenge(id:str):
    return database.GetChallenge(id)

def GetChallengeDiscord(discord:str):
    return database.GetChallengeDiscord(discord)

def CompleteChallenge(id:str):
    difficulty = database.GetChallenge(id)
    if difficulty:
        difficulty = difficulty[2]
        match difficulty:
            case ("Easy"):
                database.CompleteChallenge(id, 500)
            case("Hard"):
                database.CompleteChallenge(id, 1000)
            case("Expert+"):
                database.CompleteChallenge(id, 2000)
            case _:
                database.CompleteChallenge(id, 0)
    
def CancelChallenge(discord:str):
    player = database.LoadPlayerDiscord(discord)
    database.CompleteChallenge(player.id, 0)

def SetChallenge(discord:str, difficulty:str, type:str, points:int):
    return database.SetChallenge(discord, difficulty, type, points)

def LoadPlayerDiscord(discord:str) -> Union[classes.player, bool]:
    return database.LoadPlayerDiscord(discord)

def LoadPlayerID(id:str) -> Union[classes.player, bool]:
    return database.LoadPlayerID(id)

def RemovePlayer(discord:str):
    database.RemovePlayer(discord)

def InsertPlayer(player:classes.player):
    database.InsertPlayer(player)

def SetChannel(channel_id:str, channel_type:int):
    database.SetChannel(channel_id, channel_type)

def RemoveChannel(channel_id:str):
    database.RemoveChannel(channel_id)

def GetChannels(channel_type:int) -> list:
    return database.GetChannels(channel_type)