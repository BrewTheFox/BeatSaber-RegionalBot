import sqlite3
import classes as classes
from typing import Union

class db():
    def __init__(self, databasepath:str=".././database.db"):
        """Initialize database"""
        self.conn = sqlite3.connect(databasepath)
        self.curr = self.conn.cursor()
        self.curr.execute("CREATE TABLE IF NOT EXISTS 'top_players_ss' ('id' varchar NOT NULL, 'performance_points' real NOT NULL);")
        self.curr.execute("CREATE TABLE IF NOT EXISTS 'top_players_bl' ('id' varchar NOT NULL, 'performance_points' real NOT NULL);")
        self.curr.execute("CREATE TABLE IF NOT EXISTS 'players' ('id' varchar NOT NULL, 'discord' varchar NOT NULL, 'challenge' varchar NULL, 'points' int, 'difficulty' varchar NULL,'total_challenge_points' int NOT NULL);")
        self.curr.execute("CREATE TABLE IF NOT EXISTS 'servers' ('channel' varchar NULL, 'channel_type' int(1) NOT NULL);")
        self.conn.commit()

    def LoadPlayerDiscord(self, discord:str) -> Union[classes.player, bool]:
        """Loads a specific player data using their discord ID"""
        self.curr.execute("SELECT id, discord, challenge, points, total_challenge_points FROM players WHERE discord=?", (discord, ))
        data = self.curr.fetchone()
        if data is None:
            return False
        return classes.player(id=data[0], discord=data[1], challenge=data[2], points=data[3], total_points=data[4])
    
    def GetPlayerPP(self, platform:int, id:str) -> Union[tuple, None]:
        """Returns the player's Performance Points based on the provided ID"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.curr.execute(f"SELECT performance_points FROM {platform} WHERE id=?;", (id,))
        data = self.curr.fetchone()
        return data
    
    def UpdatePlayerPerformancePoints(self, platform:int, id:str, pp:float) -> None:
        """Updates the player's performance points using the provided ID"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.curr.execute(f"UPDATE {platform} SET performance_points=? WHERE id = ?;", (pp, id))
        self.conn.commit()
    
    def InsertTopPlayer(self, platform:int, id:str, pp:float) -> None:
        """Inserts a player into the top players table"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.curr.execute(f"SELECT performance_points FROM {platform} WHERE id=?;",(id, ))
        data = self.curr.fetchone()
        if data is not None:
            return
        self.curr.execute(f"INSERT INTO {platform}('id', 'performance_points') VALUES (?, ?);", (id, pp))
        self.conn.commit()
    
    def GetPlayersBetween(self, platform:int, InitialPP:float, NewPP:float) -> Union[tuple, None]:
        """Gets the players between an specific range of Performance Points"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.curr.execute(f"SELECT id FROM {platform} WHERE performance_points BETWEEN ? AND ?;",  (InitialPP, NewPP))
        data = self.curr.fetchall()
        return data
    
    def LoadPlayerID(self, id:int) -> Union[classes.player, bool]:
        """Loads a specific player data using their steam ID"""
        self.curr.execute("SELECT id, discord, challenge, points, total_challenge_points FROM players WHERE id=?", (id, ))
        data = self.curr.fetchone()
        if data is None:
            return False
        return classes.player(id=data[0], discord=data[1], challenge=data[2], points=data[3], total_points=data[4])
    
    def DeletePlayer(self, discord:str) -> Union[classes.player, bool]:
        """Deletes the player from the database given a Discord ID"""
        self.curr.execute("SELECT * FROM players WHERE discord=?", (discord, ))
        data = self.curr.fetchone()
        if data is None:
            return False
        self.curr.execute("DELETE FROM players WHERE discord=?", (discord, ))
        self.conn.commit()
        return True
    
    def InsertPlayer(self, player:classes.player):
        """Inserts the player into the Database"""
        self.curr.execute("INSERT INTO players (discord, id, total_challenge_points, points) VALUES (?, ?, ?, ?);", (player.discord, player.id, player.total_points, player.points))
        self.conn.commit()
    
    def SetChallenge(self, discord:str, difficulty:str, type:str, points:int) -> bool:
        """Asigns a challenge to a player given its discord id"""
        self.curr.execute("SELECT * FROM players WHERE discord=?", (discord, ))
        data = self.curr.fetchone()
        if data is None:
            return False
        self.curr.execute("UPDATE players SET challenge = ?, points = ?, difficulty = ? WHERE discord=?;", (type, points, difficulty, discord))
        self.conn.commit()
        return True
    
    def GetChallenge(self, id:str) -> list:
        """Returns the challenge assigned for a user in the format Challenge, Points, Difficulty"""
        self.curr.execute("SELECT challenge, points, difficulty FROM players WHERE id=?", (id,))
        data = self.curr.fetchone()
        if data is None:
            return [None, None, None]
        return data[0], data[1], data[2]
    
    def GetChallengeDiscord(self, discord:str) -> list:
        """Returns the challenge assigned for a user in the format Challenge, Points, Difficulty"""
        self.curr.execute("SELECT challenge, points, difficulty FROM players WHERE discord=?", (discord,))
        data = self.curr.fetchone()
        if data is None:
            return [None, None, None]
        return data[0], data[1], data[2]   

    def RemovePlayer(self, discord:str):
        """Deletes a player from the database"""
        self.curr.execute("DELETE FROM players WHERE discord=?;", (discord, ))
        self.conn.commit()

    def CompleteChallenge(self, id:str, points:int):
        """Completes the challenge of a user"""
        self.curr.execute("UPDATE players SET total_challenge_points = total_challenge_points + ?, points=NULL, difficulty=NULL, challenge=NULL WHERE id = ?;", (points, id))
        self.conn.commit()

    def RemoveChannel(self, channel_id:str):
        """Deletes a channel from the database"""
        self.curr.execute("DELETE FROM servers WHERE channel=?;", (channel_id, ))
        self.conn.commit()
    
    def SetChannel(self, channel_id:str, channel_type:int):
        """Saves the channel of certain thing on the database 0 for Challenges, 1 for Scores, 2 For Player Feed"""
        self.RemoveChannel(channel_id)
        self.curr.execute("INSERT into servers (channel, channel_type) VALUES (?, ?);", (channel_id, channel_type))
        self.conn.commit()

    def GetChannels(self, channel_type:int) -> list:
        """Retrieves all the channels in the database"""
        self.curr.execute("SELECT channel FROM servers WHERE channel_type = ?", (channel_type, ))
        data = self.curr.fetchall()
        if data is None:
            return []
        return data