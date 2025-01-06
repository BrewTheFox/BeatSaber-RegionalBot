import DataBaseConn
import classes
from typing import Union

database = DataBaseConn.db()

def GetChallenge(id:str):
    return database.GetChallenge(id)

def GetChallengeDiscord(discord:str):
    return database.GetChallenge(discord)

def CompleteChallenge(id:str):
    _, _, difficulty = database.GetChallenge(id)
    if difficulty == "Easy":
        database.CompleteChallenge(id, 500)
    if difficulty == "Hard":
        database.CompleteChallenge(id, 1000)
    if difficulty == "Expert+":
        database.CompleteChallenge(id, 2000)

def CancelChallenge(id:str):
    database.CompleteChallenge(id, 0)

def SetChallenge(discord:str, difficulty:str, type:str, points:int):
    return database.SetChallenge(discord, difficulty, type, points)

def LoadPlayerDiscord(discord:str) -> Union[classes.player, bool]:
    return database.LoadPlayerDiscord(discord)

def LoadPlayerID(id:str) -> Union[classes.player, bool]:
    return database.LoadPlayerID(id)

def InsertPlayer(player:classes.player):
    database.InsertPlayer(player)

def SetChannel(channel_id:str, channel_type:int):
    database.SetChannel(channel_id, channel_type)

def RemoveChannel(channel_id:str):
    database.RemoveChannel(channel_id)

def GetChannels(channel_type:int) -> list | bool:
    return database.GetChannels(channel_type)