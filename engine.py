from typing import Dict
from entity import Entity, get_blocking_entities
from game_messages import MessageLog, Message
from game_state import GameState

from render_functions import render_all, clear_all
from event_handler import handle_event
from loader_functions.data_loaders import save_game
from death_functions import kill_monster, kill_player
from map_objects.game_map import GameMap

import tcod
import tcod.console
import tcod.event

import settings as const


# noinspection PyTypeChecker, PyUnresolvedReferences
def play_game(player: Entity, dungeon: Dict, message_log: MessageLog, game_state: GameState,
              root_console: tcod.console.Console, offscreen_console: tcod.console.Console,
              viewport_console: tcod.console.Console, log_console: tcod.console.Console,
              status_console: tcod.console.Console, entity_console: tcod.console.Console,
              current_level: int, camera: "Camera"):

    mouse_tx, mouse_ty = 0, 0

    fov_recompute = True
    prev_game_state = game_state

    targeting_item = None

    root_console.clear()
    offscreen_console.clear()
    log_console.clear()
    viewport_console.clear()

    box_text = ""

    while True:

        if fov_recompute:
            dungeon[current_level].fov_map.compute_fov(player.x, player.y, radius=const.FOV_RADIUS,
                                                       light_walls=const.FOV_LIGHT_WALLS,
                                                       algorithm=const.FOV_ALGO)

        render_all(root_console, offscreen_console, viewport_console, status_console, log_console, entity_console,
                   player, dungeon[current_level], mouse_tx, mouse_ty, fov_recompute, message_log, box_text, game_state,
                   camera)

        fov_recompute = False
        clear_all(viewport_console, dungeon[current_level].entities, camera)
        action = handle_event(tcod.event.get(), game_state)

        exit_ = action.get("exit")
        move = action.get("move")
        wait = action.get("wait")
        pickup = action.get("pickup")
        show_inventory = action.get("show_inventory")
        drop_inventory = action.get("drop_inventory")
        inventory_index = action.get("inventory_index")
        take_stairs = action.get("take_stairs")
        level_up = action.get("level_up")
        show_character_screen = action.get("show_character_screen")
        fullscreen = action.get("fullscreen")
        mouse = action.get("mouse")
        left_click = action.get("left_click")
        right_click = action.get("right_click")
        test = action.get("test")

        player_turn_results = []

        if exit_:
            if game_state in [GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY, GameState.CHARACTER_SCREEN,
                              GameState.MESSAGE_BOX]:
                game_state = prev_game_state
            elif game_state == GameState.TARGETING:
                player_turn_results.append({"targeting_cancelled": True})
            else:
                save_game(player, dungeon, message_log, game_state, current_level)
                break

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if mouse:
            mouse_tx, mouse_ty = mouse

        if move and game_state == GameState.PLAYER_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy
            if dungeon[current_level].is_walkable(dest_x, dest_y):
                target = get_blocking_entities(dungeon[current_level].entities, dest_x, dest_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy, dungeon[current_level].entities, dungeon[current_level])

                    fov_recompute = True

                for buff in player.buffs:
                    player_turn_results.extend(buff.tick_down())

                game_state = GameState.ENEMY_TURN

        elif wait:
            for buff in player.buffs:
                player_turn_results.extend(buff.tick_down())
            game_state = GameState.ENEMY_TURN

        elif pickup and game_state == GameState.PLAYER_TURN:
            for entity in dungeon[current_level].entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message("There is nothing here to pick up.", tcod.yellow))

        elif test and game_state == GameState.PLAYER_TURN:
            # message_log.add_message(Message("This is a super-long message for testing purposes, unless you're me you should definitely not be seeing it. It's really unnecessarily long.", tcod.yellow))
            prev_game_state = game_state
            game_state = GameState.MESSAGE_BOX
            box_text = "This is a testing message box."

        if show_inventory:
            if game_state == GameState.SHOW_INVENTORY:
                game_state = prev_game_state
            else:
                prev_game_state = game_state
                game_state = GameState.SHOW_INVENTORY

        if drop_inventory:
            if game_state == GameState.DROP_INVENTORY:
                game_state = prev_game_state
            else:
                prev_game_state = game_state
                game_state = GameState.DROP_INVENTORY

        if inventory_index is not None and prev_game_state != GameState.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameState.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=dungeon[current_level].entities,
                                                                fov_map=dungeon[current_level].fov_map))
            elif game_state == GameState.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if take_stairs and game_state == GameState.PLAYER_TURN:
            for entity in dungeon[current_level].entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    if entity.stairs.direction == 1:
                        current_level += 1
                        next_level = dungeon.get(current_level)
                        if next_level is None:
                            new_map = GameMap(const.MAP_WIDTH, const.MAP_HEIGHT, dungeon_level=current_level)
                            new_map.make_map(const.MAX_ROOMS, const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE,
                                             const.MAP_WIDTH, const.MAP_HEIGHT, player)
                            new_map.entities.append(player)
                            dungeon.update({current_level: new_map})
                            player.fighter.heal(player.fighter.max_hp // 2)
                            message_log.add_message(
                                Message('You take a moment to rest, and recover your strength.', tcod.light_violet))
                        else:
                            player.x = dungeon[current_level].start_x
                            player.y = dungeon[current_level].start_y
                    elif entity.stairs.direction == -1:
                        current_level -= 1
                        player.x = dungeon[current_level].end_x
                        player.y = dungeon[current_level].end_y

                    fov_recompute = True
                    viewport_console.clear()

                    break
            else:
                message_log.add_message(Message('There are no stairs here.', tcod.yellow))

        if level_up:
            if level_up == "hp":
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == "str":
                player.fighter.base_power += 1
            elif level_up == "def":
                player.fighter.base_defense += 1

            game_state = prev_game_state

        if show_character_screen:
            prev_game_state = game_state
            game_state = GameState.CHARACTER_SCREEN

        if game_state == GameState.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=dungeon[current_level].entities,
                                                        fov_map=dungeon[current_level].fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({"targeting_cancelled": True})

        for player_turn_result in player_turn_results:
            message = player_turn_result.get("message")
            dead_entity = player_turn_result.get("dead")
            item_added = player_turn_result.get("item_added")
            item_consumed = player_turn_result.get("consumed")
            item_dropped = player_turn_result.get("item_dropped")
            equip = player_turn_result.get("equip")
            targeting = player_turn_result.get("targeting")
            targeting_cancelled = player_turn_result.get("targeting_cancelled")
            xp = player_turn_result.get("xp")

            if message is not None:
                message_log.add_message(message)

            if dead_entity is not None:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                dungeon[current_level].entities.remove(item_added)

                for buff in player.buffs:
                    player_turn_results.extend(buff.tick_down())
                game_state = GameState.ENEMY_TURN

            if item_consumed:
                for buff in player.buffs:
                    player_turn_results.extend(buff.tick_down())
                game_state = GameState.ENEMY_TURN

            if item_dropped:
                dungeon[current_level].entities.append(item_dropped)

                for buff in player.buffs:
                    player_turn_results.extend(buff.tick_down())
                game_state = GameState.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get("equipped")
                    dequipped = equip_result.get("dequipped")

                    if equipped:
                        message_log.add_message(Message(f"You equipped the {equipped.name}", ))

                    if dequipped:
                        message_log.add_message(Message(f"You dequipped the {dequipped.name}", ))

                for buff in player.buffs:
                    player_turn_results.extend(buff.tick_down())
                game_state = GameState.ENEMY_TURN

            if targeting:
                prev_game_state = GameState.PLAYER_TURN
                game_state = GameState.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = prev_game_state

                message_log.add_message(Message("Targeting cancelled."))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message(f"You gain {xp} experience points!"))

                if leveled_up:
                    message_log.add_message(Message(
                        f"Your battle skills grow stronger! You reached level {player.level.current_level}!",
                        tcod.yellow))
                    prev_game_state = game_state
                    game_state = GameState.LEVEL_UP

        if game_state == GameState.ENEMY_TURN:
            for entity in dungeon[current_level].entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, dungeon[current_level],
                                                             dungeon[current_level].entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get("message")
                        dead_entity = enemy_turn_result.get("dead")

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameState.PLAYER_DEAD:
                                break
                    if game_state == GameState.PLAYER_DEAD:
                        break
                if game_state == GameState.PLAYER_DEAD:
                    break
            else:
                game_state = GameState.PLAYER_TURN
