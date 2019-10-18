from enum import Enum, auto
from typing import List, Dict, Union
from game_messages import Message


class BuffType(Enum):
    POWER = auto()
    DEFENSE = auto()
    MAX_HP = auto()


class Buff:
    def __init__(self, buff_type: BuffType, bonus: int = 0, num_turns: int = 1):
        self.buff_type = buff_type
        self.num_turns = num_turns
        self.bonus = bonus

    def to_json(self) -> Dict:
        json_data = {
            "buff_type": self.buff_type.value,
            "num_turns": self.num_turns,
            "bonus": self.bonus
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Buff", None]:
        if json_data is None:
            return None

        buff_type = BuffType(json_data["buff_type"])
        num_turns = json_data["num_turns"]
        bonus = json_data["bonus"]

        return Buff(buff_type, bonus, num_turns)

    def tick_down(self) -> List:
        self.num_turns -= 1

        results = []

        if self.num_turns <= 0:
            if self.buff_type == BuffType.POWER:
                results.append({'message': Message("You feel your strength return to normal.", (255, 255, 0))})
            elif self.buff_type == BuffType.DEFENSE:
                results.append({'message': Message("You feel your skin return to normal.", (255, 255, 0))})
            else:
                results.append({'message': Message("You feel your health return to normal.", (255, 255, 0))})

            self.owner.remove_buff(self)
            if self.buff_type == BuffType.MAX_HP:
                if self.owner.fighter.hp > self.owner.fighter.max_hp:
                    self.owner.fighter.hp = self.owner.fighter.max_hp

        return results

