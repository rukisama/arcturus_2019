import tcod
from game_messages import Message

from game_state import GameState
from entity import Entity, EntityType


def kill_player(player: "Entity"):
    player.glyph = ord('%')
    player.fg = (255, 0, 0)

    return Message("You died!", (255, 0, 0)), GameState.PLAYER_DEAD


def kill_monster(monster: "Entity"):
    death_message = Message(f"{monster.name.capitalize()} is dead!", (255, 165, 0))

    monster.glyph = ord('%')
    monster.fg = (255, 0, 0)
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"remains of {monster.name}"
    monster.entity_type = EntityType.CORPSE

    return death_message
