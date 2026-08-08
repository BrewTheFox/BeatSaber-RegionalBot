import json

with open(".././config.json", "r") as config:
    configuration = json.loads(config.read())


def get_configuration() -> dict:
    global configuration
    return configuration


def get_string(name: str, field: str = "ProfileRequest") -> str:
    return configuration["Strings"][field][name]
