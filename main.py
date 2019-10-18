import tcod
import tcod.event
import tcod.console
from loader_functions.init_new_game import get_game_variables
from menu import main_menu, message_box
from event_handler import handle_main_menu
from game_state import GameState
from engine import play_game
from camera import Camera

from loader_functions.data_loaders import load_game

import settings as const


def main() -> None:

    tcod.console_set_custom_font('potash_10x10.png',
                                 tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW)

    root_console = tcod.console_init_root(w=const.SCREEN_WIDTH,
                                          h=const.SCREEN_HEIGHT,
                                          title=const.WINDOW_TITLE,
                                          fullscreen=False,
                                          order="F",
                                          vsync=False,
                                          renderer=tcod.RENDERER_OPENGL2)

    offscreen_console = tcod.console.Console(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, order="F")

    viewport_console = tcod.console.Console(const.VIEWPORT_WIDTH, const.VIEWPORT_HEIGHT,
                                            order="F")

    status_console = tcod.console.Console(const.STATUS_WIDTH, const.STATUS_HEIGHT, order="F")

    entity_console = tcod.console.Console(const.ENTITY_WIDTH, const.ENTITY_HEIGHT, order="F")

    log_console = tcod.console.Console(const.LOG_WIDTH, const.LOG_HEIGHT, order="F")

    root_console.ch[:] = 0
    root_console.fg[:] = (255, 255, 255)
    root_console.bg[:] = (0, 0, 0)

    offscreen_console.ch[:] = 0
    offscreen_console.fg[:] = (255, 255, 255)
    offscreen_console.bg[:] = (0, 0, 0)

    viewport_console.ch[:] = 0
    viewport_console.fg[:] = (255, 255, 255)
    viewport_console.bg[:] = (0, 0, 0)

    status_console.ch[:] = 0
    status_console.fg[:] = (255, 255, 255)
    status_console.bg[:] = (0, 0, 0)

    entity_console.ch[:] = 0
    entity_console.fg[:] = (255, 255, 255)
    entity_console.bg[:] = (0, 0, 0)

    player = None
    dungeon = None
    message_log = None
    game_state = None
    camera = None

    show_main_menu = True
    show_load_error = False
    show_corrupt_error = False

    current_level = -1

    while True:

        if show_main_menu:
            main_menu(root_console, "heic1104a-edited.png", const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
            if show_load_error:
                message_text = "No save exists."
                message_box(root_console, message_text, len(message_text), const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
            if show_corrupt_error:
                message_text = "Corrupt save."
                message_box(root_console, message_text, len(message_text), const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

            tcod.console_flush()

            action = handle_main_menu(tcod.event.get())

            new_game = action.get("new_game")
            load_save = action.get("load_game")
            exit_game = action.get("exit")

            if show_load_error and (new_game or load_save or exit_game):
                show_load_error = False
            elif show_corrupt_error and (new_game or load_save or exit_game):
                show_corrupt_error = False
            elif new_game:
                player, dungeon, message_log, game_state, current_level, camera = get_game_variables()
                game_state = GameState.PLAYER_TURN

                show_main_menu = False

            elif load_save:
                try:
                    camera = Camera(0, 0, const.VIEWPORT_WIDTH - 1, const.VIEWPORT_HEIGHT - 1)
                    player, dungeon, message_log, game_state, current_level = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error = True
                except KeyError:
                    show_corrupt_error = True
            elif exit_game:
                break

        else:
            root_console.clear()
            assert current_level != -1
            play_game(player, dungeon, message_log, game_state, root_console, offscreen_console,
                      viewport_console, log_console, status_console, entity_console, current_level, camera)

            show_main_menu = True


if __name__ == '__main__':
    main()
