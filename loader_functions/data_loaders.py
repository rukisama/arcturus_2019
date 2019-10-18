import os
import json
from typing import Dict
from entity import Entity
from map_objects.game_map import GameMap
from game_messages import MessageLog
from game_state import GameState


def save_game(player: Entity, dungeon: Dict, message_log: MessageLog, game_state: GameState, current_level: int):
    with open("save_data", mode="w") as f:
        dungeon[current_level].entities.remove(player)
        game_data = {
            "player": player.to_json(),
            "dungeon": {dungeon_level: game_map.to_json() for dungeon_level, game_map in dungeon.items()},
            "message_log": message_log.to_json(),
            "game_state": game_state.value,
            "current_level": current_level
        }

        json.dump(game_data, f)


def load_game():
    if not os.path.isfile("save_data"):
        raise FileNotFoundError

    with open("save_data", mode="r") as f:
        json_data = json.load(f)

        player = Entity.from_json(json_data["player"])
        dungeon = {int(dungeon_level): GameMap.from_json(map_data) for dungeon_level, map_data in json_data["dungeon"].items()}
        message_log = MessageLog.from_json(json_data["message_log"])
        game_state = GameState(json_data["game_state"])
        current_level = int(json_data["current_level"])

        dungeon[current_level].entities.append(player)

        return player, dungeon, message_log, game_state, current_level
