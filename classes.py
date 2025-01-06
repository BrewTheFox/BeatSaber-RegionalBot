
class player():
    def __init__(self, id:int, discord:str, challenge:str | None, total_points:int ,points:int | None):
        self.id = id
        self.discord = discord
        self.challenge = challenge
        self.points = points
        self.total_points = total_points
