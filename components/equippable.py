from typing import Dict, Union
from equipment_slots import EquipmentSlots


class Equippable:
    def __init__(self, slot: EquipmentSlots, power_bonus: int = 0, defense_bonus: int = 0, max_hp_bonus: int = 0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

    def to_json(self) -> Dict:
        json_data = {
            "slot": self.slot.value,
            "power_bonus": self.power_bonus,
            "defense_bonus": self.defense_bonus,
            "max_hp_bonus": self.max_hp_bonus
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Equippable", None]:
        if json_data is None:
            return None

        slot = EquipmentSlots(json_data["slot"])
        power_bonus = json_data["power_bonus"]
        defense_bonus = json_data["defense_bonus"]
        max_hp_bonus = json_data["max_hp_bonus"]

        return Equippable(slot, power_bonus, defense_bonus, max_hp_bonus)
