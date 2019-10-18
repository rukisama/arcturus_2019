import numpy as np
import json
from random import randint
from math import sqrt
from typing import List, Dict

import tcod
import tcod.map

from entity import Entity, EntityType

from map_objects.rect import Rect
from map_objects.tile_map import TileMap

from components.fighter import Fighter
from components.ai import BasicMonster
from components.item import Item
from components.stairs import Stairs
from components.equipment import EquipmentSlots
from components.equippable import Equippable

from random_utils import from_dungeon_level, random_choice_from_dict
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse, buff
from game_messages import MessageLog, Message
import charmap as ch

map_dtype = np.dtype([("glyph", np.intc), ("fg", "(3,)i4"), ("bg", "(3,)i4")])


class GameMap:
    def __init__(self, map_width: int, map_height: int, dungeon_level: int = 1):
        self.width = map_width
        self.height = map_height
        self.dungeon_level = dungeon_level
        self.entities = []
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        self.tile_map = TileMap(self.width, self.height)
        self.fov_map = tcod.map.Map(self.width, self.height, order="F")
        self.explored = np.zeros((self.width, self.height), dtype=bool, order="F")

        self.fov_map.walkable[:] = False
        self.fov_map.transparent[:] = False

    def to_json(self) -> Dict:
        json_data = {
            "width": self.width,
            "height": self.height,
            "tile_map": self.tile_map.to_json(),
            "fov_map_transparent": self.fov_map.transparent.tolist(),
            "fov_map_walkable": self.fov_map.walkable.tolist(),
            "fov_map_fov": self.fov_map.fov.tolist(),
            "explored": self.explored.tolist(),
            "dungeon_level": self.dungeon_level,
            "entities": [entity.to_json() for entity in self.entities]
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> "GameMap":
        width = json_data["width"]
        height = json_data["height"]
        tile_map = TileMap.from_json(json_data["tile_map"])
        fov_transparent = np.array(json_data["fov_map_transparent"])
        fov_walkable = np.array(json_data["fov_map_walkable"])
        fov_fov = np.array(json_data["fov_map_fov"])
        explored = np.array(json_data["explored"])
        dungeon_level = json_data["dungeon_level"]
        entities = [Entity.from_json(entity_data) for entity_data in json_data["entities"]]

        loaded_map = GameMap(width, height)
        loaded_map.tile_map = tile_map
        loaded_map.fov_map.transparent[:] = fov_transparent[:]
        loaded_map.fov_map.walkable[:] = fov_walkable[:]
        loaded_map.fov_map.fov[:] = fov_fov[:]
        loaded_map.explored = explored
        loaded_map.dungeon_level = dungeon_level
        loaded_map.entities = entities

        return loaded_map

    def make_map(self, max_rooms: int, room_min_size: int, room_max_size: int, map_width: int,
                 map_height: int, player: Entity):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)

            x = randint(0, map_width - w - 2)
            y = randint(0, map_height - h - 2)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break

            else:
                self.dig_room(new_room)

                new_x, new_y = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                    self.start_x = new_x
                    self.start_y = new_y
                else:
                    other = find_nearest_room(new_room, rooms)

                    prev_x, prev_y = other.center()
                    # new_x, new_y = new_room.center()

                    # print(f"\t\tNearest room to {(new_x, new_y)} is {(prev_x, prev_y)}")

                    if randint(0, 1) == 1:
                        self.dig_h_tunnel(new_x, prev_x, new_y)
                        self.dig_v_tunnel(prev_x, prev_y, new_y)
                    else:
                        self.dig_v_tunnel(new_x, new_y, prev_y)
                        self.dig_h_tunnel(new_x, prev_x, prev_y)

                if num_rooms > 0:
                    self.place_entities(new_room)

                rooms.append(new_room)
                num_rooms += 1

        self.end_x = center_of_last_room_x
        self.end_y = center_of_last_room_y

        down_stairs_component = Stairs(1)
        down_stairs = Entity("Stairs", EntityType.STAIRS, center_of_last_room_x, center_of_last_room_y, ord('>'),
                             (255, 255, 255), stairs=down_stairs_component)
        self.entities.append(down_stairs)

        if self.dungeon_level > 1:
            up_stairs_component = Stairs(-1)
            up_stairs = Entity("Stairs", EntityType.STAIRS, player.x, player.y, ord('<'),
                               (255, 255, 255), stairs=up_stairs_component)
            self.entities.append(up_stairs)

    def dig_h_tunnel(self, x1: int, x2: int, y: int) -> None:
        start_x = min(x1, x2)
        end_x = max(x1, x2)
        self.fov_map.walkable[start_x:end_x + 1, y] = True
        self.fov_map.transparent[start_x:end_x + 1, y] = True
        self.tile_map.glyph[start_x:end_x + 1, y] = 0

    def dig_v_tunnel(self, x: int, y1: int, y2: int) -> None:
        start_y = min(y1, y2)
        end_y = max(y1, y2)
        self.fov_map.walkable[x, start_y:end_y + 1] = True
        self.fov_map.transparent[x, start_y:end_y + 1] = True
        self.tile_map.glyph[x, start_y:end_y + 1] = 0

    def dig_room(self, room: Rect):
        self.fov_map.walkable[room.x1 + 1:room.x2, room.y1 + 1:room.y2] = True
        self.fov_map.transparent[room.x1 + 1:room.x2, room.y1 + 1:room.y2] = True
        self.tile_map.glyph[room.x1 + 1:room.x2, room.y1 + 1:room.y2] = 0

    def place_entities(self, room: Rect):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        with open("items.json", mode='r') as f:
            items_data = json.load(f)
            # print(items_data)
            items = [item for item in items_data["items"]]
            # for item in items:
            #     print(f'{item["id"]} {item["chance"]}')
            item_chances = {item["id"]: from_dungeon_level([item["chance"]], self.dungeon_level) for item in items}

        monster_chances = {
            "orc": 80,
            "troll": from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
        }

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == "orc":
                    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_component = BasicMonster()
                    monster = Entity("Orc", EntityType.ACTOR, x, y, ord('o'), tcod.desaturated_green, blocks=True,
                                     fighter=fighter_component, ai=ai_component)
                else:
                    fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_component = BasicMonster()
                    monster = Entity("Troll", EntityType.ACTOR, x, y, ord('T'), tcod.darker_green, blocks=True,
                                     fighter=fighter_component, ai=ai_component)

                self.entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)
                chosen_item = None
                for item in items_data["items"]:
                    if item["id"] == item_choice:
                        if item["targeting_message"]:
                            targeting_message = Message(item["targeting_message"]["text"],
                                                        item["targeting_message"]["color"])
                        else:
                            targeting_message = None

                        if item["use_function"]:
                            use_function = eval(item["use_function"])
                        else:
                            use_function = None

                        if item["function_kwargs"]:
                            item_component = Item(use_function=use_function, targeting=item["targeting"],
                                                  targeting_message=targeting_message, **item["function_kwargs"])
                        else:
                            item_component = Item(use_function=use_function, targeting=item["targeting"],
                                                  targeting_message=targeting_message)

                        if item["equippable"]:
                            equippable_component = Equippable(EquipmentSlots(item["equippable"]["slot"]),
                                                              power_bonus=item["equippable"]["power_bonus"],
                                                              defense_bonus=item["equippable"]["defense_bonus"],
                                                              max_hp_bonus=item["equippable"]["max_hp_bonus"])
                        else:
                            equippable_component = None

                        chosen_item = Entity(item["name"], EntityType.ITEM, x, y, ord(item["glyph"]), fg=item["color"],
                                             item=item_component, equippable=equippable_component)
                # if item_choice == "healing_potion":
                #     item_component = Item(use_function=heal, amount=40)
                #     item = Entity("Healing Potion", EntityType.ITEM, x, y, ord('!'), fg=tcod.violet,
                #                   item=item_component)
                # elif item_choice == "sword":
                #     equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                #     item = Entity("Sword", EntityType.ITEM, x, y, ord('/'), fg=tcod.sky,
                #                   equippable=equippable_component)
                # elif item_choice == "shield":
                #     equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                #     item = Entity("Shield", EntityType.ITEM, x, y, ord('['), fg=tcod.darker_orange,
                #                   equippable=equippable_component)
                # elif item_choice == "fireball_scroll":
                #     item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                #        'Left-click a target tile for the fireball, or right-click to cancel.', tcod.light_cyan),
                #                          damage=25, radius=3)
                #     item = Entity("Fireball Scroll", EntityType.ITEM, x, y, ord('#'), fg=tcod.orange,
                #                   item=item_component)
                # elif item_choice == "confusion_scroll":
                #     item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                #        'Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan))
                #     item = Entity("Confusion Scroll", EntityType.ITEM, x, y, ord('#'), fg=tcod.light_pink,
                #                   item=item_component)
                # else:
                #     item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                #     item = Entity("Lightning Scroll", EntityType.ITEM, x, y, ord('#'), fg=tcod.yellow,
                #                   item=item_component)

                self.entities.append(chosen_item)

    def is_walkable(self, x, y) -> bool:
        return self.fov_map.walkable[x, y]

    def take_stairs(self, player: Entity, message_log: MessageLog, constants: Dict, dungeon: Dict,
                    direction: int) -> None:
        assert (direction == -1 or direction == 1), "Invalid Direction"
        if direction == 1:
            self.dungeon_level += 1
            self.entities = [player]

            self.fov_map = tcod.map.Map(self.width, self.height, order="F")
            self.explored = np.zeros((self.width, self.height), dtype=bool)

            self.fov_map.walkable[:] = False
            self.fov_map.transparent[:] = False

            self.make_map(constants["max_rooms"], constants["room_min_size"], constants["room_max_size"],
                          constants["map_width"], constants["map_height"], player)

            player.fighter.heal(player.fighter.max_hp // 2)

            dungeon.update({self.dungeon_level: self})

            message_log.add_message(Message('You take a moment to rest, and recover your strength.', tcod.light_violet))

        else:
            pass


def find_nearest_room(room: Rect, others: List[Rect]) -> Rect:
    nearest = room
    shortest_distance = 10000
    for other in others:
        x, y = room.center()
        o_x, o_y = other.center()
        if shortest_distance > distance(x, y, o_x, o_y) and x != o_x and y != o_y:
            shortest_distance = distance(x, y, o_x, o_y)
            nearest = other

    # print(f"\t\tNearest room to {room.center()} is {nearest.center()}")
    return nearest


def distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return int(sqrt((x2 - x1)**2 + (y2 - y1)**2))
