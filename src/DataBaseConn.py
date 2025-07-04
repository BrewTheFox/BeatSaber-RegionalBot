import sqlite3
from typing import Union, Optional

class db():
    def __init__(self, databasepath:str=".././database.db"):
        """Initialize database"""
        self.conn = sqlite3.connect(databasepath)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS 'top_players_ss' ('id' varchar NOT NULL, 'performance_points' real NOT NULL);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS 'top_players_bl' ('id' varchar NOT NULL, 'performance_points' real NOT NULL);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS 'challenges' ('challengerID' varchar NOT NULL, 'challengedID' varchar NOT NULL, 'songID' varchar NOT NULL, 'firstcompleter' varchar, 'firstscore' int);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS 'players' ('id' varchar NOT NULL, 'discord' varchar NOT NULL, 'total_challenge_points' int NOT NULL);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS 'servers' ('channel' varchar NULL, 'channel_type' int(1) NOT NULL);")
        self.MigratePlayers()
        self.conn.commit()

    def MigratePlayers(self) -> None:
        self.cur.execute("PRAGMA table_info(players);")
        columns = self.cur.fetchall()
        try:
            for column in columns:
                if column[1] == "challenge":
                    self.cur.execute("SELECT id, discord FROM players;")
                    data = self.cur.fetchall()
                    self.cur.execute("BEGIN TRANSACTION;")
                    self.cur.execute("DROP TABLE players;")
                    self.cur.execute("CREATE TABLE IF NOT EXISTS 'players' ('id' varchar NOT NULL, 'discord' varchar NOT NULL, 'total_challenge_points' int NOT NULL);")
                    for player in data:
                        self.cur.execute("INSERT INTO players('id', 'discord', total_challenge_points) VALUES (?, ?, 0);", (player[0], player[1]))
                    self.conn.commit()
                    return
        except:
            self.conn.rollback()
            
    def LoadPlayerDiscord(self, discord:str) -> Union[tuple, bool]:
        """Loads a specific player data using their discord ID"""
        self.cur.execute("SELECT id, discord, total_challenge_points FROM players WHERE discord=?", (discord, ))
        data = self.cur.fetchone()
        if data is None:
            return False
        return list(data)
    
    def LeaderboardTop(self) -> Optional[tuple]:
        self.cur.execute("SELECT discord, total_challenge_points FROM players ORDER BY total_challenge_points DESC LIMIT 5;")
        return self.cur.fetchall()

    def UpdateChallenge(self, id:str, score:str) -> None:
        """Updates the challenge first completer and firstscore values"""
        self.cur.execute("SELECT * FROM challenges WHERE challengerID=?", (id, ))
        data = self.cur.fetchone()
        if data is not None:
            self.cur.execute("UPDATE challenges SET firstcompleter=?, firstscore=? WHERE challengerID=?;", (id, score, id))
        self.cur.execute("SELECT * FROM challenges WHERE challengedID=?", (id, ))
        data = self.cur.fetchone()
        if data is not None:
            self.cur.execute("UPDATE challenges SET firstcompleter=?, firstscore=? WHERE challengedID=?;", (id, score, id))
        self.conn.commit()
    
    def GetPlayerPP(self, platform:int, id:str) -> Optional[tuple]:
        """Returns the player's Performance Points based on the provided ID"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.cur.execute(f"SELECT performance_points FROM {platform} WHERE id=?;", (id,))
        data = self.cur.fetchone()
        return data
    
    def UpdatePlayerPerformancePoints(self, platform:int, id:str, pp:float) -> None:
        """Updates the player's performance points using the provided ID"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.cur.execute(f"UPDATE {platform} SET performance_points=? WHERE id = ?;", (pp, id))
        self.conn.commit()
    
    def InsertTopPlayer(self, platform:int, id:str, pp:float) -> None:
        """Inserts a player into the top players table"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.cur.execute(f"SELECT performance_points FROM {platform} WHERE id=?;",(id, ))
        data = self.cur.fetchone()
        if data is not None:
            return
        self.cur.execute(f"INSERT INTO {platform}('id', 'performance_points') VALUES (?, ?);", (id, pp))
        self.conn.commit()
    
    def GetPlayersBetween(self, platform:int, InitialPP:float, NewPP:float) -> Optional[tuple]:
        """Gets the players between an specific range of Performance Points"""
        platform = "top_players_ss" if platform == 0 else "top_players_bl"
        self.cur.execute(f"SELECT id FROM {platform} WHERE performance_points BETWEEN ? AND ? AND performance_points != 0;",  (InitialPP, NewPP))
        data = self.cur.fetchall()
        return data
    
    def LoadPlayerID(self, id:int) -> Union[list, bool]:
        """Loads a specific player data using their steam ID"""
        self.cur.execute("SELECT id, discord, total_challenge_points FROM players WHERE id=?", (id, ))
        data = self.cur.fetchone()
        if data is None:
            return False
        return list(data)
    
    def DeletePlayer(self, discord:str) -> Union[tuple, bool]:
        """Deletes the player from the database given a Discord ID"""
        self.cur.execute("SELECT id FROM players WHERE discord=?", (discord, ))
        id = self.cur.fetchone()
        if id is None:
            return False
        id = id[0]
        self.cur.execute("DELETE FROM players WHERE discord=?", (discord, ))
        self.cur.execute("SELECT * from challenges WHERE challengerID=?;", (id, ))
        data = self.cur.fetchone()
        if data:
            self.cur.execute("DELETE FROM challenges WHERE challengerID=?", (id, ))
        self.cur.execute("SELECT * from challenges WHERE challengedID=?;", (id, ))
        data = self.cur.fetchone()
        if data:
            self.cur.execute("DELETE FROM challenges WHERE challengedID=?", (id, ))
        self.conn.commit()
        return True
    
    def InsertPlayer(self, discord:str, id:str):
        """Inserts the player into the Database"""
        self.cur.execute("INSERT INTO players (discord, id, total_challenge_points) VALUES (?, ?, 0);", (discord, id))
        self.conn.commit()
    
    def SetChallenge(self, challenged:str, challenger:str, songID:str) -> bool:
        """Asigns a challenge to a player given its discord id"""
        self.cur.execute("SELECT * FROM challenges WHERE challengerID=?", (challenger, ))
        data = self.cur.fetchone()
        if data is not None:
            return False
        self.cur.execute("SELECT * FROM challenges WHERE challengedID=?", (challenged, ))
        data = self.cur.fetchone()
        if data is not None:
            return False
        self.cur.execute("INSERT INTO challenges ('challengerID', 'challengedID', 'songID') VALUES (?,?,?);", (challenger, challenged, songID))
        self.conn.commit()
        return True
    
    def CompleteChallenge(self, WinnerID:str) -> None:
        """Completes a challenge and adds a point to the winner"""
        self.AddChallengePoint(WinnerID, 1)
        self.cur.execute("SELECT * FROM challenges WHERE challengerID=?", (WinnerID, ))
        data = self.cur.fetchone()
        if data is not None:
            self.cur.execute("DELETE FROM challenges WHERE challengerID=?", (WinnerID,))
        self.cur.execute("SELECT * FROM challenges WHERE challengedID=?", (WinnerID, ))
        data = self.cur.fetchone()
        if data is not None:
            self.cur.execute("DELETE FROM challenges WHERE challengedID=?", (WinnerID,))
        self.conn.commit()
    
    def GetChallenge(self, id:str) -> list:
        """Returns the challenge assigned for a user in the format challengedID, songID, firstscore, firstcompleter"""
        self.cur.execute("SELECT challengerID, songID, firstscore, firstcompleter FROM challenges WHERE challengedID=?", (id,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0], data[1], data[2], data[3]
        self.cur.execute("SELECT challengedID, songID, firstscore, firstcompleter FROM challenges WHERE challengerID=?", (id,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0], data[1], data[2], data[3]
        return [None, None, None, None]
    
    def GetChallengeDiscord(self, discord:str) -> list:
        """Returns the challenge assigned for a user in the format challengedID, songID, firstscore, firstcompleter"""
        id = self.LoadPlayerDiscord(discord)[0]
        self.cur.execute("SELECT challengerID, songID, firstscore, firstcompleter FROM challenges WHERE challengedID=?", (id,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0], data[1], data[2], data[3]
        self.cur.execute("SELECT challengedID, songID, firstscore, firstcompleter FROM challenges WHERE challengerID=?", (id,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0], data[1], data[2], data[3]
        return [None, None, None, None]

    def CancelChallenge(self, discord:str):
        """Cancels the challenge of a user given its discord ID"""
        id = self.LoadPlayerDiscord(discord)[0]
        self.cur.execute("SELECT challengedID from challenges WHERE challengerID=?;", (id, ))
        data = self.cur.fetchone()
        if data:
            self.cur.execute("DELETE FROM challenges WHERE challengerID=?", (id, ))
            self.conn.commit()
            self.AddChallengePoint(data[0], 1)
            self.AddChallengePoint(id, -1)
        self.cur.execute("SELECT challengerID from challenges WHERE challengedID=?;", (id, ))
        if data:
            self.cur.execute("DELETE FROM challenges WHERE challengedID=?", (id, ))
            self.conn.commit()
            self.AddChallengePoint(data[0], 1)
            self.AddChallengePoint(id, -1)
        data = self.cur.fetchone()
        return True
    
    def AddChallengePoint(self, PlayerID:str, Ammount:int):
        """Adds Challenge Points to a player"""
        self.cur.execute("UPDATE players SET total_challenge_points = total_challenge_points + ? WHERE id = ?;", (Ammount, PlayerID))
        self.conn.commit()

    def RemoveChannel(self, channel_id:str):
        """Deletes a channel from the database"""
        self.cur.execute("DELETE FROM servers WHERE channel=?;", (channel_id, ))
        self.conn.commit()
    
    def SetChannel(self, channel_id:str, channel_type:int):
        """Saves the channel of certain thing on the database 0 for Challenges, 1 for Scores, 2 For Player Feed"""
        self.RemoveChannel(channel_id)
        self.cur.execute("INSERT into servers (channel, channel_type) VALUES (?, ?);", (channel_id, channel_type))
        self.conn.commit()

    def GetChannels(self, channel_type:int) -> list:
        """Retrieves all the channels in the database"""
        self.cur.execute("SELECT channel FROM servers WHERE channel_type = ?", (channel_type, ))
        data = self.cur.fetchall()
        if data is None:
            return []
        return data