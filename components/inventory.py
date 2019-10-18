from typing import List, Dict, Union
import tcod

from game_messages import Message


class Inventory:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.items = []

    def to_json(self) -> Dict:
        json_data = {
            "capacity": self.capacity,
            "items": [item.to_json() for item in self.items]
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["Inventory", None]:
        return None
        # if json_data is not None:
        #     capacity = json_data["capacity"]
        #     inventory = Inventory(capacity)
        #
        #     return inventory

    def add_item(self, item: "Entity") -> List:
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                "item_added": None,
                "message": Message("You cannot carry any more.", tcod.yellow)
            })
        else:
            results.append({
                "item_added": item,
                "message": Message(f"You pick up the {item.name}", tcod.light_blue)
            })

            self.items.append(item)

        return results

    def use(self, item_entity: "Entity", **kwargs) -> List:
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({"equip": item_entity})
            else:
                results.append({"message": Message(f"The {item_entity.name} cannot be used.")})
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({"targeting": item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get("consumed"):
                        self.remove_item(item_entity)

                results.extend(item_use_results)

        return results

    def remove_item(self, item: "Entity") -> None:
        self.items.remove(item)

    def drop_item(self, item) -> List:
        results = []

        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({"item_dropped": item,
                        "message": Message(f"You dropped the {item.name}", tcod.yellow)})

        return results
