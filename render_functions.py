import tcod
import tcod.console
import tcod.map
from typing import List, Tuple
import numpy as np

from entity import Entity, EntityType
from map_objects.game_map import GameMap
from game_messages import MessageLog
from game_state import GameState
from menu import inventory_menu, level_up_menu, character_screen, message_box
import charmap as ch

import settings as const


SHOW_STATS = True


def render_bar(panel: tcod.console.Console, x: int, y: int, total_width: int, name: str, value: int, maximum: int,
               bar_color: Tuple[int, int, int], back_color: Tuple[int, int, int]):
    bar_width = int(float(value) / maximum * total_width)

    panel.bg[x:x+total_width, y] = back_color

    if bar_width > 0:
        panel.bg[x:x+bar_width, y] = bar_color

    bar_str = f"{name}: {value}/{maximum}"
    px = x + ((total_width // 2) - (len(bar_str) // 2))
    panel.print(px, y, bar_str, fg=(255, 255, 255))


def get_names_under_mouse(mx: int, my: int, entities: List[Entity], game_map):
    names = [entity.name for entity in entities if entity.x == mx and entity.y == my and
             game_map.fov_map.fov[mx, my]]

    names = ', '.join(names)

    return names.capitalize()


# noinspection PyUnresolvedReferences
def render_all(root_console: tcod.console.Console,
               offscreen_console: tcod.console.Console,
               viewport_console: tcod.console.Console,
               status_console: tcod.console.Console,
               log_console: tcod.console.Console,
               entity_console: tcod.console.Console,
               player: Entity, game_map: GameMap, mouse_tx: int, mouse_ty: int,
               fov_recompute: bool, game_messages: MessageLog, box_text: str,
               game_state: GameState, camera: "Camera") -> None:

    screen_height = const.SCREEN_HEIGHT
    screen_width = const.SCREEN_WIDTH
    bar_width = const.BAR_WIDTH

    status_console.clear()
    log_console.clear()
    entity_console.clear()

    if fov_recompute:

        # Show nothing by default
        viewport_console.ch[:] = 0
        viewport_console.fg[:] = (0, 0, 0)
        viewport_console.bg[:] = (0, 0, 0)

        # Move camera to follow the player
        camera.move_camera(player.x, player.y, game_map.width, game_map.height)
        cam_x, cam_y = camera.x, camera.y
        cam_x2, cam_y2 = camera.x2, camera.y2

        # Translate map coordinates to camera coordinates
        cam_fov = game_map.fov_map.fov[cam_x:cam_x2+1, cam_y:cam_y2+1]
        cam_explored = game_map.explored[cam_x:cam_x2+1, cam_y:cam_y2+1]
        cam_glyph = game_map.tile_map.glyph[cam_x:cam_x2+1, cam_y:cam_y2+1]
        cam_fg = game_map.tile_map.fg[cam_x:cam_x2+1, cam_y:cam_y2+1]
        cam_bg = game_map.tile_map.bg[cam_x:cam_x2 + 1, cam_y:cam_y2 + 1]

        # If a tile is explored but not visible, render it in dark colors.
        viewport_console.fg[cam_explored == True] = np.multiply(cam_fg[cam_explored == True], 0.50).astype(np.int)
        viewport_console.bg[cam_explored == True] = np.multiply(cam_bg[cam_explored == True], 0.50).astype(np.int)
        viewport_console.ch[cam_explored == True] = cam_glyph[cam_explored == True]

        # If a tile is visible then render it in light colors.
        viewport_console.fg[cam_fov == True] = cam_fg[cam_fov == True]
        viewport_console.bg[cam_fov == True] = cam_bg[cam_fov == True]
        viewport_console.ch[cam_fov == True] = cam_glyph[cam_fov == True]
        # viewport_console.ch[cam_transparent == False] = 178

        # If a tile is visible, then it is now explored.
        game_map.explored[game_map.fov_map.fov == True] = True

    # Draw all entities in the list
    entities_in_render_order = sorted(game_map.entities, key=lambda x: x.entity_type.value)

    for entity in entities_in_render_order:
        draw_entity(viewport_console, entity, game_map, camera)

    render_bar(status_console, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               tcod.light_red, tcod.darker_red)
    status_console.print(1, 3, f"Dungeon Level: {game_map.dungeon_level}")

    status_console.print(1, 0, get_names_under_mouse(mouse_tx, mouse_ty, game_map.entities, game_map),
                         fg=(128, 128, 128))

    y = 0
    for message in game_messages.messages:
        log_console.print(game_messages.x, y, message.text, fg=message.color)
        y += 1

    entity_console.print(5, 0, "Visible:", (128, 128, 128))

    visible_entities = [entity for entity in entities_in_render_order if tcod.map_is_in_fov(game_map.fov_map, entity.x,
                                                                                            entity.y)]

    for index, entity in enumerate(visible_entities, start=1):
        if entity.entity_type not in [EntityType.PLAYER, EntityType.CORPSE]:
            entity_str = f"{chr(entity.glyph)}: {entity.name.capitalize()}"
            entity_console.print(1, index, entity_str, entity.fg)

    draw_frames(offscreen_console)

    # offscreen_console.print(0, screen_height - 1, f"{mouse_tx}, {mouse_ty}")

    viewport_console.blit(offscreen_console, 1, 1)
    status_console.blit(offscreen_console, const.VIEWPORT_WIDTH + 2, 1)
    log_console.blit(offscreen_console, 1, const.VIEWPORT_HEIGHT + 2)
    entity_console.blit(offscreen_console, const.VIEWPORT_WIDTH + 2, const.STATUS_HEIGHT + 2)
    offscreen_console.blit(root_console)

    if game_state in [GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY]:
        if game_state == GameState.SHOW_INVENTORY:
            inventory_title = "Press the key next to an item to use it, ESC to cancel.\n"
        else:
            inventory_title = "Press the key next to an item to drop it, ESC to cancel.\n"

        inventory_menu(root_console, inventory_title, player, 50, screen_width, screen_height)

    elif game_state == GameState.LEVEL_UP:
        level_up_menu(root_console, "Level up! Choose a stat to raise:", player, 40, screen_width, screen_height)

    elif game_state == GameState.CHARACTER_SCREEN:
        character_screen(root_console, player, 30, 10, screen_width, screen_height)

    elif game_state == GameState.MESSAGE_BOX:
        message_box(root_console, box_text, len(box_text), const.VIEWPORT_WIDTH, const.VIEWPORT_HEIGHT)

    if SHOW_STATS:
        fps = tcod.sys_get_fps()
        if fps > 0:
            fps_str = f"FPS: {fps} ({1000 / fps:.2f} ms/frame)"
            root_console.print(0, const.SCREEN_HEIGHT - 1, fps_str, fg=(255, 255, 255))

    tcod.console_flush()


# noinspection PyUnresolvedReferences
def clear_all(viewport_console: tcod.console.Console, entities: List, camera: "Camera"):
    for entity in entities:
        x, y = camera.to_camera_coordinates(entity.x, entity.y)
        # print(x, y)
        if x is not None and y is not None:
            viewport_console.ch[x, y] = 0


# noinspection PyUnresolvedReferences
def draw_entity(offscreen_console: tcod.console.Console, entity: Entity, game_map: GameMap, camera: "Camera"):
    x, y = camera.to_camera_coordinates(entity.x, entity.y)

    if tcod.map_is_in_fov(game_map.fov_map, entity.x, entity.y) or (entity.stairs and game_map.explored[entity.x, entity.y]):
        if x is not None and y is not None:
            offscreen_console.tiles2[x, y] = (entity.glyph, entity.fg, game_map.tile_map.default_bg)

        if entity.stairs and not tcod.map_is_in_fov(game_map.fov_map, entity.x, entity.y):
            if x is not None and y is not None:
                offscreen_console.bg[x, y] = np.multiply(game_map.tile_map.default_bg, 0.50).astype(np.int)


def clear_entity(offscreen_console, entity):
    # erase the character that represents this object
    offscreen_console.ch[entity.x, entity.y] = ord(' ')


def draw_frames(console: tcod.console.Console):
    colors = (tcod.grey, tcod.black)
    vp_width = const.VIEWPORT_WIDTH
    vp_height = const.VIEWPORT_HEIGHT
    sc_width = const.SCREEN_WIDTH
    sc_height = const.SCREEN_HEIGHT

    st_height = const.STATUS_HEIGHT

    # Horizontal lines
    console.tiles2[1:sc_width - 1, 0] = (ch.DOUBLE_HORIZONTAL, *colors)
    console.tiles2[1:vp_width + 1, vp_height + 1] = (ch.DOUBLE_HORIZONTAL, *colors)
    console.tiles2[1:sc_width - 1, sc_height - 1] = (ch.DOUBLE_HORIZONTAL, *colors)
    console.tiles2[vp_width + 1:sc_width, st_height + 1] = (ch.DOUBLE_HORIZONTAL, *colors)

    # Vertical lines
    console.tiles2[0, 1:sc_height - 1] = (ch.DOUBLE_VERTICAL, *colors)
    console.tiles2[vp_width + 1, 1:sc_height - 1] = (ch.DOUBLE_VERTICAL, *colors)
    console.tiles2[sc_width - 1, 1:sc_height - 1] = (ch.DOUBLE_VERTICAL, *colors)

    # Corners and junctions
    console.tiles2[0, 0] = (ch.DOUBLE_TOP_LEFT, *colors)
    console.tiles2[0, sc_height - 1] = (ch.DOUBLE_BOTTOM_LEFT, *colors)
    console.tiles2[sc_width - 1, 0] = (ch.DOUBLE_TOP_RIGHT, *colors)
    console.tiles2[sc_width - 1, sc_height - 1] = (ch.DOUBLE_BOTTOM_RIGHT, *colors)
    console.tiles2[vp_width + 1, 0] = (ch.DOUBLE_T_BOTTOM, *colors)
    console.tiles2[vp_width + 1, vp_height + 1] = (ch.DOUBLE_T_LEFT, *colors)
    console.tiles2[0, vp_height + 1] = (ch.DOUBLE_T_RIGHT, *colors)
    console.tiles2[vp_width + 1, sc_height - 1] = (ch.DOUBLE_T_TOP, *colors)
    console.tiles2[vp_width + 1, st_height + 1] = (ch.DOUBLE_T_RIGHT, *colors)
    console.tiles2[sc_width - 1, st_height + 1] = (ch.DOUBLE_T_LEFT, *colors)
