from typing import Dict, Union


class Level:
    def __init__(self, current_level: int = 1, current_xp: int = 0, level_up_base: int = 200,
                 level_up_factor: int = 150):
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor

    @property
    def experience_to_next_level(self) -> int:
        return self.level_up_base + self.current_level * self.level_up_factor

    def add_xp(self, xp: int) -> bool:
        self.current_xp += xp

        if self.current_xp > self.experience_to_next_level:
            self.current_xp -= self.experience_to_next_level
            self.current_level += 1

            return True
        else:
            return False

    def to_json(self) -> Dict:
        json_data = {
            "current_level": self.current_level,
            "current_xp": self.current_xp,
            "level_up_base": self.level_up_base,
            "level_up_factor": self.level_up_factor
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Level", None]:
        if json_data is None:
            return None

        current_level = json_data["current_level"]
        current_xp = json_data["current_xp"]
        level_up_base = json_data["level_up_base"]
        level_up_factor = json_data["level_up_factor"]

        return Level(current_level, current_xp, level_up_base, level_up_factor)
