import json

with open(".././config.json", "r") as config:
    configuration = json.loads(config.read())

def GetConfiguration() -> dict:
    global configuration
    return configuration

def GetString(name:str, field:str = "ProfileRequest") -> str:
    return configuration["Strings"][field][name]