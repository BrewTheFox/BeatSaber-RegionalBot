import DataBaseConn as DataBaseConn
from typing import Union, Optional

database = DataBaseConn.db()

def GetChallenge(id:str):
    return database.GetChallenge(id)

def GetChallengeDiscord(discord:str):
    return database.GetChallengeDiscord(discord)

def UpdateChallenge(id:str, score:str) -> None:
    return database.UpdateChallenge(id, score)

def LeaderboardTop() -> Optional[tuple]:
    return database.LeaderboardTop()

def CompleteChallenge(id:str):
    return database.CompleteChallenge(id)
    
def CancelChallenge(discord:str):
    database.CancelChallenge(discord)

def SetChallenge(challenged:str, challenger:str, songID:str) -> bool:
    return database.SetChallenge(challenged, challenger, songID)

def LoadPlayerDiscord(discord:str) -> Union[list, bool]:
    return database.LoadPlayerDiscord(discord)

def LoadPlayerID(id:str) -> Union[list, bool]:
    return database.LoadPlayerID(id)

def InsertPlayer(discord:str, id:str):
    database.InsertPlayer(discord, id)

def DeletePlayer(discord:str):
    database.DeletePlayer(discord)

def SetChannel(channel_id:str, channel_type:int):
    database.SetChannel(channel_id, channel_type)

def RemoveChannel(channel_id:str):
    database.RemoveChannel(channel_id)

def GetChannels(channel_type:int) -> list:
    return database.GetChannels(channel_type)

def GetPlayerPP(platform:int, id:str) -> tuple:
    return database.GetPlayerPP(platform, id)

def UpdatePlayerPerformancePoints(platform:int, id:str, pp:float) -> None:
    return database.UpdatePlayerPerformancePoints(platform, id, pp)

def InsertTopPlayer(platform:int, id:str, pp:float) -> None:
    database.InsertTopPlayer(platform, id, pp)

def GetPlayersBetween(platform:int, InitialPP:float, NewPP:float) -> Optional[tuple]:
    return database.GetPlayersBetween(platform, InitialPP, NewPP)