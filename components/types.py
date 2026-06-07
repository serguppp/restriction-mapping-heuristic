from enum import Enum
import json


class States(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "pasued"


def map_text_to_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def map_list_to_string(list: list) -> str:
    return ", ".join(map(str, list))


def dump_json(list: list) -> str:
    return json.dumps(list, separators=(",", ":"))
