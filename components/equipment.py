from typing import List, Dict, Union
from equipment_slots import EquipmentSlots


class Equipment:
    def __init__(self, main_hand=None, off_hand=None):
        self.main_hand = main_hand
        self.off_hand = off_hand

    def to_json(self) -> Dict:
        json_data = {
            "main_hand": self.main_hand.to_json() if self.main_hand is not None else None,
            "off_hand": self.off_hand.to_json() if self.off_hand is not None else None
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Equipment", None]:
        return None
        # if json_data is None:
        #     return None
        # main_hand_data = json_data["main_hand"]
        # off_hand_data = json_data["off_hand"]
        #
        # if main_hand_data:
        #     main_hand = Entity.from_json(main_hand_data)
        # else:
        #     main_hand = None
        #
        # if off_hand_data:
        #     off_hand = Entity.from_json(off_hand_data)
        # else:
        #     off_hand = None
        #
        # return Equipment(main_hand, off_hand)

    @property
    def max_hp_bonus(self) -> int:
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus

        return bonus

    @property
    def power_bonus(self) -> int:
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.power_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.power_bonus

        return bonus

    @property
    def defense_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.defense_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.defense_bonus

        return bonus

    def toggle_equip(self, equippable_entity: "Entity") -> List:
        results = []

        slot = equippable_entity.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equippable_entity:
                self.main_hand = None
                results.append({"dequipped": equippable_entity})
            else:
                if self.main_hand:
                    results.append({"dequipped": self.main_hand})

                self.main_hand = equippable_entity
                results.append({"equipped": equippable_entity})
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equippable_entity:
                self.off_hand = None
                results.append({"dequipped": equippable_entity})
            else:
                if self.off_hand:
                    results.append({"dequipped": self.off_hand})

                self.off_hand = equippable_entity
                results.append({"equipped": equippable_entity})

        return results
