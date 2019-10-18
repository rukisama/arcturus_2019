from typing import List, Dict, Union
from game_messages import Message
from components.buff import BuffType


# noinspection PyUnresolvedReferences
class Fighter:
    def __init__(self, hp: int, defense: int, power: int, xp: int = 0):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    def to_json(self) -> Dict:
        json_data = {
            "base_max_hp": self.base_max_hp,
            "current_hp": self.hp,
            "base_defense": self.base_defense,
            "base_power": self.base_power,
            "xp": self.xp
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Fighter", None]:
        if json_data is not None:
            base_max_hp = json_data["base_max_hp"]
            current_hp = json_data["current_hp"]
            base_defense = json_data["base_defense"]
            base_power = json_data["base_power"]
            xp = json_data["xp"]

            fighter = Fighter(base_max_hp, base_defense, base_power, xp=xp)
            fighter.hp = current_hp
            fighter.base_max_hp = base_max_hp
            fighter.base_defense = base_defense
            fighter.base_power = base_power

            return fighter

        return None

    @property
    def max_hp(self) -> int:
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        for buff in self.owner.buffs:
            if buff.buff_type == BuffType.MAX_HP:
                bonus += buff.bonus

        return self.base_max_hp + bonus

    @property
    def power(self) -> int:
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        for buff in self.owner.buffs:
            if buff.buff_type == BuffType.POWER:
                bonus += buff.bonus

        return self.base_power + bonus

    @property
    def defense(self) -> int:
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        for buff in self.owner.buffs:
            if buff.buff_type == BuffType.DEFENSE:
                bonus += buff.bonus

        return self.base_defense + bonus

    def take_damage(self, amount: int) -> List:
        results = []
        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner, "xp": self.xp})

        return results

    def attack(self, target: "Entity") -> List:
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            results.append({'message': Message(f"{self.owner.name.capitalize()} attacks {target.name.capitalize()} for {damage} HP of damage!", (255, 255, 255))})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message(f"{self.owner.name.capitalize()} attacks {target.name.capitalize()}, but does no damage.", (255, 255, 255))})

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp
