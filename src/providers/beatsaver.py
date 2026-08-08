import aiohttp
import json


async def song_info(hash: str, dificulty: str) -> dict:
    session = aiohttp.ClientSession()
    async with session as ses:
        async with ses.get(f"https://api.beatsaver.com/maps/hash/{hash}") as request:
            data = json.loads(await request.text())
    try:
        if not "error" in data.keys():
            difficulty = dificulty.strip("_").split("_")
            for difficulties in data["versions"][0]["diffs"]:
                if (
                    difficulties["difficulty"].lower() == difficulty[0].lower()
                    and difficulties["characteristic"] in difficulty[1]
                ):
                    return {
                        "cover": data["versions"][0]["coverURL"],
                        "notes": difficulties["notes"],
                        "bombs": difficulties["bombs"],
                        "difficulty": difficulties["difficulty"],
                        "id": data["id"],
                        "name": data["name"],
                    }
            return {
                "cover": "https://cdn.scoresaber.com/avatars/steam.png",
                "notes": 0,
                "bombs": 0,
                "difficulty": "Unknown",
                "id": "00000",
                "name": "Song not found!",
                "error": True,
            }
    except:
        return {
            "cover": "https://cdn.scoresaber.com/avatars/steam.png",
            "notes": 0,
            "bombs": 0,
            "difficulty": "Unknown",
            "id": "00000",
            "name": "Song not found / Problematic!",
            "error": True,
        }

    return data


async def song_exists(id: str) -> list:
    session = aiohttp.ClientSession()
    async with session as ses:
        async with ses.get(f"https://api.beatsaver.com/maps/id/{id}") as request:
            data = json.loads(await request.text())
    try:
        if not "success" in data.keys():
            return [
                True,
                data["metadata"]["songName"],
                data["versions"][-1]["coverURL"],
            ]
        else:
            return [False]
    except:
        return [False]
