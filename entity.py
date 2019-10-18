from typing import Tuple, List, Any, Dict, Union
from components.fighter import Fighter
from components.item import Item
from components.inventory import Inventory
from components.ai import get_ai
from components.stairs import Stairs
from components.level import Level
from components.equippable import Equippable
from components.equipment import Equipment
from components.buff import Buff
import math
from enum import Enum, auto


class EntityType(Enum):
    CORPSE = auto()
    ITEM = auto()
    STAIRS = auto()
    ACTOR = auto()
    PLAYER = auto()


class Entity:
    """ A generic entity to represent the player, npcs, items, etc. """
    def __init__(self, name: str, entity_type: EntityType, x: int, y: int, glyph: int,
                 fg: Tuple[int, int, int] = (255, 255, 255), bg: Tuple[int, int, int] = (0, 0, 0), blocks: bool = False,
                 fighter: Fighter = None, ai: Any = None, item: Item = None, inventory: Inventory = None,
                 stairs: Stairs = None, level: Level = None, equipment: Equipment = None,
                 equippable: Equippable = None):
        self.name = name
        self.entity_type = entity_type
        self.x = x
        self.y = y
        self.glyph = glyph
        self.fg = fg
        self.bg = bg
        self.blocks = blocks
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable
        self.buffs = []

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.level:
            self.level.owner = self

        if self.equipment:
            self.equipment.owner = self

        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

    def to_json(self) -> Dict:
        json_data = {
            "name": self.name,
            "entity_type": self.entity_type.value,
            "x": self.x,
            "y": self.y,
            "glyph": self.glyph,
            "fg": self.fg,
            "bg": self.bg,
            "blocks": self.blocks,
            "fighter": self.fighter.to_json() if self.fighter is not None else None,
            "ai": self.ai.to_json() if self.ai is not None else None,
            "item": self.item.to_json() if self.item is not None else None,
            "inventory": self.inventory.to_json() if self.inventory is not None else None,
            "stairs": self.stairs.to_json() if self.stairs is not None else None,
            "level": self.level.to_json() if self.level is not None else None,
            "equipment": self.equipment.to_json() if self.equipment is not None else None,
            "equippable": self.equippable.to_json() if self.equippable is not None else None,
            "buffs": [buff.to_json() for buff in self.buffs]
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> "Entity":
        name = json_data["name"]
        entity_type = EntityType(json_data["entity_type"])
        x = json_data["x"]
        y = json_data["y"]
        glyph = json_data["glyph"]
        fg = json_data["fg"]
        bg = json_data["bg"]
        blocks = json_data["blocks"]
        fighter = Fighter.from_json(json_data["fighter"])
        ai = get_ai(json_data["ai"])
        item = Item.from_json(json_data["item"])
        # This seems to be necessary to avoid circular imports, since inventories are full of Entities:
        inv_data = json_data["inventory"]
        if inv_data is not None:
            inv_capacity_data = inv_data["capacity"]
            inv_items_data = inv_data["items"]
            inventory = Inventory(capacity=inv_capacity_data)
            inventory.items = [Entity.from_json(item_data) for item_data in inv_items_data]
        else:
            inventory = None
        stairs = Stairs.from_json(json_data["stairs"])
        level = Level.from_json(json_data["level"])
        # This is also necessary to avoid circular imports:
        equipment_data = json_data["equipment"]
        if equipment_data is not None:
            main_hand_data = equipment_data["main_hand"]
            off_hand_data = equipment_data["off_hand"]
            main_hand = Entity.from_json(main_hand_data) if main_hand_data is not None else None
            off_hand = Entity.from_json(off_hand_data) if off_hand_data is not None else None
            equipment = Equipment(main_hand, off_hand)
        else:
            equipment = None
        equippable = Equippable.from_json(json_data["equippable"])
        buffs = [Buff.from_json(buff_data) for buff_data in json_data["buffs"]]

        entity = Entity(name, entity_type, x, y, glyph, fg, bg, blocks, fighter, ai, item, inventory, stairs, level,
                        equipment, equippable)

        for buff in buffs:
            buff.owner = entity

        entity.buffs = buffs

        return entity

    def move(self, dx: int, dy: int, entities: List["Entity"],
             game_map: "GameMap", ignore_blocking: bool = False) -> None:
        if ignore_blocking:
            self.x += dx
            self.y += dy
        else:
            if (game_map.is_walkable(self.x + dx, self.y + dy) and
                    not get_blocking_entities(entities, self.x + dx, self.y + dy)):
                self.x += dx
                self.y += dy

    def move_towards(self, target_x: int, target_y: int, game_map: "GameMap", entities: List["Entity"]):
        dx = target_x - self.x

        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if (game_map.is_walkable(self.x + dx, self.y + dy) and
                not get_blocking_entities(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy, entities, game_map)

    def add_buff(self, buff: Buff):
        self.buffs.append(buff)

    def remove_buff(self, buff: Buff):
        self.buffs.remove(buff)

    def distance_to(self, other) -> float:
        dx = other.x - self.x
        dy = other.y - self.y

        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, tx, ty):
        return math.sqrt((tx - self.x) ** 2 + (ty - self.y) ** 2)


def get_blocking_entities(entities: List, dest_x: int, dest_y: int) -> Union[Entity, None]:
    for entity in entities:
        if entity.blocks and entity.x == dest_x and entity.y == dest_y:
            return entity

    return None
