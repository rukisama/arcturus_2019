from typing import Dict, Union
from game_messages import Message
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse, buff


class Item:
    def __init__(self, use_function=None, targeting=False, targeting_message=None, **kwargs):
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs

    def to_json(self) -> Dict:
        json_data = {
            "use_function": self.use_function.__name__ if self.use_function is not None else None,
            "targeting": self.targeting,
            "targeting_message": self.targeting_message.to_json() if self.targeting_message is not None else None,
            "function_kwargs": self.function_kwargs
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Item", None]:
        if json_data is None:
            return None

        use_function = eval(json_data["use_function"]) if json_data["use_function"] is not None else None
        targeting = json_data["targeting"]
        targeting_message = Message.from_json(json_data["targeting_message"])
        function_kwargs = json_data["function_kwargs"]

        item = Item(use_function=use_function, targeting=targeting, targeting_message=targeting_message,
                    **function_kwargs)

        return item
