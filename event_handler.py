import tcod.event
from typing import Iterable, Dict
from game_state import GameState


def handle_event(events: Iterable, game_state: GameState) -> Dict:
    for event in events:
        if event.type == "QUIT":
            return {"exit": True}
        elif event.type == "KEYDOWN" and game_state == GameState.PLAYER_TURN:
            return handle_player_turn_keys(event)
        elif event.type == "KEYDOWN" and game_state == GameState.PLAYER_DEAD:
            return handle_player_dead_keys(event)
        elif event.type == "KEYDOWN" and game_state in [GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY]:
            return handle_inventory_keys(event)
        elif event.type == "KEYDOWN" and game_state == GameState.TARGETING:
            return handle_targeting(event)
        elif event.type == "KEYDOWN" and game_state == GameState.LEVEL_UP:
            return handle_level_up_menu(event)
        elif event.type == "KEYDOWN" and game_state == GameState.CHARACTER_SCREEN:
            return handle_character_screen(event)
        elif event.type == "KEYDOWN" and game_state == GameState.MESSAGE_BOX:
            return handle_any_key()
        elif event.type in ["MOUSEMOTION", "MOUSEBUTTONDOWN"]:
            return handle_mouse(event)

    return {}


def handle_any_key() -> Dict:
    return {"exit": True}


def handle_main_menu(events: Iterable) -> Dict:
    for event in events:
        if event.type == "KEYDOWN":
            if event.sym == tcod.event.K_a:
                return {"new_game": True}
            elif event.sym == tcod.event.K_b:
                return {"load_game": True}
            elif event.sym == tcod.event.K_c or event.sym == tcod.event.K_ESCAPE:
                return {"exit": True}

    return {}


def handle_level_up_menu(key: tcod.event.KeyboardEvent) -> Dict:

    if key.sym == tcod.event.K_a:
        return {"level_up": "hp"}
    elif key.sym == tcod.event.K_b:
        return {"level_up": "str"}
    elif key.sym == tcod.event.K_c:
        return {"level_up": "def"}

    return {}


def handle_character_screen(key: tcod.event.KeyboardEvent) -> Dict:
    if key.sym == tcod.event.K_ESCAPE:
        return {"exit": True}
    elif key.sym == tcod.event.K_c:
        return {"exit": True}

    return {}


def handle_targeting(key: tcod.event.KeyboardEvent) -> Dict:
    if key.sym == tcod.event.K_ESCAPE:
        return {"exit": True}

    return {}


def handle_player_turn_keys(key: tcod.event.KeyboardEvent) -> Dict:
    # Movement keys
    if key.sym in [tcod.event.K_UP, tcod.event.K_k, tcod.event.K_KP_8]:
        return {'move': (0, -1)}
    elif key.sym in [tcod.event.K_u, tcod.event.K_KP_9]:
        return {"move": (1, -1)}
    elif key.sym in [tcod.event.K_y, tcod.event.K_KP_7]:
        return {"move": (-1, -1)}
    elif key.sym in [tcod.event.K_DOWN, tcod.event.K_j, tcod.event.K_KP_2]:
        return {'move': (0, 1)}
    elif key.sym in [tcod.event.K_n, tcod.event.K_KP_3]:
        return {"move": (1, 1)}
    elif key.sym in [tcod.event.K_b, tcod.event.K_KP_1]:
        return {"move": (-1, 1)}
    elif key.sym in [tcod.event.K_LEFT, tcod.event.K_h, tcod.event.K_KP_4]:
        return {'move': (-1, 0)}
    elif key.sym in [tcod.event.K_RIGHT, tcod.event.K_l, tcod.event.K_KP_6]:
        return {'move': (1, 0)}

    if key.sym == tcod.event.K_g:
        return {'pickup': True}
    elif key.sym == tcod.event.K_i:
        return {"show_inventory": True}
    elif key.sym == tcod.event.K_d:
        return {"drop_inventory": True}
    elif key.sym == tcod.event.K_RETURN:
        return {"take_stairs": True}
    elif key.sym == tcod.event.K_c:
        return {"show_character_screen": True}
    elif key.sym in [tcod.event.K_z, tcod.event.K_KP_5]:
        return {"wait": True}
    elif key.sym == tcod.event.K_BACKQUOTE:
        return {"test": True}

    if key.sym == tcod.event.K_RETURN and key.mod & tcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.sym == tcod.event.K_ESCAPE:
        # Exit the menu or game.
        return {'exit': True}

    # No key was pressed
    return {}


def handle_player_dead_keys(key: tcod.event.KeyboardEvent) -> Dict:
    if key.sym == tcod.event.K_i:
        return {"show_inventory": True}

    if key.sym == tcod.event.K_RETURN and key.mod & tcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.sym == tcod.event.K_ESCAPE:
        # Exit the menu or game.
        return {'exit': True}

    return {}


def handle_inventory_keys(key: tcod.event.KeyboardEvent) -> Dict:

    index = key.sym - ord('a')

    if index >= 0:
        return {"inventory_index": index}

    if key.sym == tcod.event.K_RETURN and key.mod & tcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.sym == tcod.event.K_ESCAPE:
        # Exit the menu or game.
        return {'exit': True}

    return {}


def handle_mouse(event: tcod.event.Event) -> Dict:
    if event.type == "MOUSEBUTTONDOWN":
        if event.button == tcod.event.BUTTON_LEFT:
            return {"left_click": event.tile}
        elif event.button == tcod.event.BUTTON_RIGHT:
            return {"right_click": event.tile}

    else:
        return {"mouse": event.tile}



