from typing import List, Dict
import tcod
import tcod.path
from random import randint
from game_messages import Message
from enum import Enum, auto


class AIType(Enum):
    BasicMonster = auto()
    ConfusedMonster = auto()


def get_ai(json_data):
    if json_data is None:
        return None
    search_type = json_data["ai_type"]

    if search_type == AIType.BasicMonster.value:
        ai = BasicMonster()
    elif search_type == AIType.ConfusedMonster.value:
        prev_ai = get_ai(json_data["prev_ai"])
        num_turns = json_data["num_turns"]
        ai = ConfusedMonster(prev_ai, num_turns)
    else:
        ai = None

    return ai


# noinspection PyUnresolvedReferences
class BasicMonster:
    def __init__(self):
        self.ai_type = AIType.BasicMonster

    def to_json(self) -> Dict:
        json_data = {
            "ai_type": self.ai_type.value
        }

        return json_data

    def take_turn(self, target: "Entity", game_map: "GameMap", entities: List["Entity"]) -> List:
        results = []

        monster = self.owner
        if tcod.map_is_in_fov(game_map.fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                astar = tcod.path.AStar(game_map.fov_map.walkable)
                dest_x, dest_y = astar.get_path(monster.x, monster.y, target.x, target.y)[0]
                dx = dest_x - monster.x
                dy = dest_y - monster.y
                monster.move(dx, dy, entities, game_map)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results


# noinspection PyUnresolvedReferences
class ConfusedMonster:
    def __init__(self, prev_ai, num_turns: int = 10):
        self.ai_type = AIType.ConfusedMonster
        self.prev_ai = prev_ai
        self.num_turns = num_turns

    def to_json(self) -> Dict:
        json_data = {
            "ai_type": self.ai_type.value,
            "prev_ai": self.prev_ai.to_json(),
            "num_turns": self.num_turns
        }

        return json_data

    def take_turn(self, target: "Entity", game_map: "GameMap", entities: List["Entity"]) -> List:
        results = []

        if self.num_turns > 0:
            rand_x = self.owner.x + randint(0, 2) - 1
            rand_y = self.owner.y + randint(0, 2) - 1

            if rand_x != self.owner.x and rand_y != self.owner.y:
                self.owner.move_towards(rand_x, rand_y, game_map, entities)

            self.num_turns -= 1
        else:
            self.owner.ai = self.prev_ai
            self.prev_ai.owner = self.owner
            results.append({"message": Message(f"The {self.owner.name} is no longer confused!", tcod.red)})

        return results
