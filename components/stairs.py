from typing import Dict, Union


class Stairs:
    def __init__(self, direction: int):
        self.direction = direction

    def to_json(self) -> Dict:
        json_data = {
            "direction": self.direction
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Stairs", None]:
        if json_data is None:
            return None

        direction = json_data["direction"]

        return Stairs(direction)
