import tcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment
from components.equippable import Equippable
from equipment_slots import EquipmentSlots

from camera import Camera

from entity import Entity, EntityType

from game_messages import MessageLog

from game_state import GameState

from map_objects.game_map import GameMap

import settings as const


def get_constants():
    window_title = "Arcturus"

    screen_width = 96
    screen_height = 54

    viewport_width = int(screen_width * 0.79)
    viewport_height = int(screen_height * 0.75)

    status_width = screen_width - viewport_width - 3
    status_height = screen_height // 3

    entity_width = screen_width - viewport_width - 3
    entity_height = screen_height - status_height - 3

    bar_width = status_width - 2

    log_width = viewport_width
    log_height = screen_height - viewport_height - 3

    map_width = 75
    map_height = 75

    room_max_size = 10
    room_min_size = 6
    max_rooms = 10000

    fov_algo = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        'dark_wall': (0, 0, 100),
        'dark_ground': (50, 50, 150),
        'light_wall': (130, 110, 50),
        'light_ground': (200, 180, 50)
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'viewport_width': viewport_width,
        'viewport_height': viewport_height,
        'status_width': status_width,
        'status_height': status_height,
        "entity_width": entity_width,
        "entity_height": entity_height,
        'log_width': log_width,
        'log_height': log_height,
        'bar_width': bar_width,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algo': fov_algo,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'colors': colors
    }

    return constants


def get_game_variables():
    fighter_component = Fighter(hp=100, defense=1, power=2)
    inventory_component = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()
    player = Entity(name="Player", entity_type=EntityType.PLAYER, x=const.SCREEN_WIDTH // 2,
                    y=const.SCREEN_HEIGHT // 2, glyph=ord('@'),
                    fg=(255, 255, 255), blocks=True, fighter=fighter_component,
                    inventory=inventory_component, level=level_component, equipment=equipment_component)

    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    dagger = Entity("Dagger", EntityType.ITEM, 0, 0, ord('-'), fg=tcod.sky, equippable=equippable_component)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    dungeon = {}
    game_map = GameMap(const.MAP_WIDTH, const.MAP_HEIGHT)
    game_map.make_map(const.MAX_ROOMS, const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE,
                      const.MAP_WIDTH, const.MAP_HEIGHT, player)
    game_map.entities.append(player)
    dungeon.update({game_map.dungeon_level: game_map})

    message_log = MessageLog(0, const.LOG_WIDTH, const.LOG_HEIGHT)

    game_state = GameState.PLAYER_TURN

    camera = Camera(0, 0, const.VIEWPORT_WIDTH - 1, const.VIEWPORT_HEIGHT - 1)

    current_level = 1

    return player, dungeon, message_log, game_state, current_level, camera
