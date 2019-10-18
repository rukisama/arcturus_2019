from typing import List
import tcod
import tcod.console

from entity import Entity


def menu(console: tcod.console.Console, header: str, options: List, width: int,
         screen_width: int, screen_height: int, sy: int = -1, fg_alpha: float = 1.0, bg_alpha: float = 0.3):

    if len(options) > 26:
        raise ValueError("Cannot have menu with more than 26 options.")

    if len(header) == 0:
        header_height = 0
    else:
        header_height = console.get_height_rect(0, 0, width, screen_height, header)
    height = len(options) + header_height

    window = tcod.console.Console(width, height, order="F")

    window.print_box(0, 0, width, height, header, fg=(255, 255, 255), bg=(0, 0, 0))

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = f"({chr(letter_index)}) {option_text}"
        window.print(0, y, text, fg=(255, 255, 255))
        y += 1
        letter_index += 1

    x = int(screen_width / 2 - width / 2)
    if sy == -1:
        y = int(screen_height / 2 - height / 2)
    else:
        y = sy

    window.blit(console, x, y, fg_alpha=fg_alpha, bg_alpha=bg_alpha)


def inventory_menu(console: tcod.console.Console, header: str, player: Entity,
                   inventory_width: int, screen_width: int, screen_height: int) -> None:

    if len(player.inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = []

        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append(f"{item.name} (in main hand)")
            elif player.equipment.off_hand == item:
                options.append(f"{item.name} (in off hand)")
            else:
                options.append(item.name)

    menu(console, header, options, inventory_width, screen_width, screen_height)


def main_menu(console: tcod.console.Console, bg_image: str, screen_width: int, screen_height: int) -> None:
    console.clear()

    bg_image = tcod.image_load(bg_image)
    bg_image.blit_2x(console, 0, 0)

    title_con = tcod.console_from_xp("arcturus.xp")

    title_con.blit(console, 24, 24, bg_alpha=0.0)

    menu(console, "", ["New Game", "Load Game", "Quit"], 13, screen_width, screen_height, sy=31)


def level_up_menu(console: tcod.console.Console, header: str, player: Entity, menu_width: int, screen_width: int,
                  screen_height: int):
    options = [f"Constitution (+20 HP, from {player.fighter.max_hp})",
               f"Strength (+1 attack, from {player.fighter.power})",
               f"Agility (+1 defense, from {player.fighter.defense})"]

    menu(console, header, options, menu_width, screen_width, screen_height)


def character_screen(console: tcod.console.Console, player: Entity, character_screen_width: int,
                     character_screen_height: int, screen_width: int, screen_height: int):
    window = tcod.console.Console(character_screen_width, character_screen_height, order="F")

    window.fg[:] = (255, 255, 255)
    window.bg[:] = (0, 0, 0)
    window.ch[:] = 0

    window.print(0, 1, "Character Information")
    window.print(0, 2, f"Level: {player.level.current_level}")
    window.print(0, 3, f"Experience: {player.level.current_xp}")
    window.print(0, 4, f"Experience to Next Level: {player.level.experience_to_next_level}")
    window.print(0, 6, f"Maximum HP: {player.fighter.max_hp}")
    window.print(0, 7, f"Attack: {player.fighter.power}")
    window.print(0, 8, f"Defense: {player.fighter.defense}")

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2

    window.blit(console, x, y, fg_alpha=1.0, bg_alpha=0.7)


def message_box(console: tcod.console.Console, header: str, width: int, screen_width: int, screen_height: int) -> None:
    menu(console, header, [], width, screen_width, screen_height, fg_alpha=1.0, bg_alpha=0.7)
