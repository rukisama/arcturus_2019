#!/usr/bin/env python3
# To the extent possible under law, the Kyle Stewart has waived all
# copyright and related or neighboring rights for this script.  This work is
# published from: United States.
# https://creativecommons.org/publicdomain/zero/1.0/
import random
import math

import tcod
import tcod.event
import tcod.tileset

import numpy as np

WIDTH, HEIGHT = 96, 54

BLOCKS = {
    # 1: upper-left, 2: upper-right, 4: lower-left, 8: lower-right
    tcod.CHAR_SUBP_NW: 1,
    tcod.CHAR_SUBP_NE: 2,
    tcod.CHAR_SUBP_N: 1 | 2,
    tcod.CHAR_SUBP_SE: 8,
    tcod.CHAR_SUBP_DIAG: 1 | 8,
    tcod.CHAR_SUBP_E: 2 | 8,
    tcod.CHAR_SUBP_SW: 4,
    0x2588: 1 | 2 | 4 | 8,
    0x2596: 4,
    0x2597: 8,
    0x2598: 1,
    0x2599: 1 | 4 | 8,
    0x259A: 1 | 8,
    0x259B: 1 | 2 | 4,
    0x259C: 1 | 2 | 8,
    0x259D: 2,
    0x259E: 2 | 4,
    0x259F: 2 | 4 | 8,
}


def generate_quadrants():
    """Generate quadrant block elements, overwriting the current font.

    Call this after your font is loaded.
    """
    ts = tcod.tileset.get_default()
    half_w = ts.tile_width // 2
    half_h = ts.tile_height // 2
    for codepoint, quads in BLOCKS.items():
        tile = np.zeros(ts.tile_shape, np.uint8)
        tile[:half_h, :half_w] = 255 if quads & 1 else 0
        tile[:half_h, half_w:] = 255 if quads & 2 else 0
        tile[half_h:, :half_w] = 255 if quads & 4 else 0
        tile[half_h:, half_w:] = 255 if quads & 8 else 0
        ts.set_tile(codepoint, tile)


class Dot:
    def __init__(self):
        self.reset()
        for _ in range(random.randint(0, 150)):
            self.step()

    def reset(self):
        self.pos = (54, 96)
        direction = random.uniform(0, math.tau)
        speed = random.uniform(.0001, 0.001)
        self.speed = math.sin(direction) * speed, math.cos(direction) * speed
        post = random.uniform(0, 50)
        self.pos = self.pos[0] + math.sin(direction) * post, self.pos[1] + math.cos(direction) * post

    def step(self):
        self.pos = self.pos[0] + self.speed[0], self.pos[1] + self.speed[1]
        self.speed = self.speed[0] * 1.5, self.speed[1] * 1.5
        if not (0 <= self.pos[0] < HEIGHT * 2 and 0 <= self.pos[1] < WIDTH * 2):
            self.reset()

    def draw(self, pad):
        line = np.array(tcod.line_where(
            round(self.pos[0]), round(self.pos[1]), round(self.pos[0] + self.speed[0]), round(self.pos[1] + self.speed[1]))).T[:-1].T
        line = line.T[line[0] < HEIGHT * 2].T
        line = line.T[line[1] < WIDTH * 2].T
        line = line.T[line[0] >= 0].T
        line = line.T[line[1] >= 0].T
        if not line.size:
            return
        vis = 255
        pad[tuple(line)] |= np.linspace(vis // 2, vis, line.shape[1], dtype=np.uint8)[:, np.newaxis]


def main():
    """Example program for tcod.event"""
    TITLE = None

    tcod.console_set_custom_font(
        "potash_10x10.png", tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW
    )

    generate_quadrants()

    with tcod.console_init_root(
        WIDTH,
        HEIGHT,
        TITLE,
        order="F",
        renderer=tcod.RENDERER_SDL2,
        vsync=True,
    ) as console:
        # tcod.sys_set_fps(30)
        pad = np.zeros((HEIGHT * 2, WIDTH * 2, 3), np.uint8)
        dots = [Dot() for _ in range(200)]
        while True:
            pad[...] //= 2
            for dot in dots:
                dot.draw(pad)
                dot.step()

            console.draw_semigraphics(pad)
            console.print(0, HEIGHT-1, str(tcod.sys_get_fps()), fg=(255, 255, 255), bg=(0, 0, 0))
            tcod.console_flush()
            for event in tcod.event.get():
                if event.type == "QUIT" or (event.type == "KEYDOWN" and event.sym == tcod.event.K_ESCAPE):
                    raise SystemExit()


if __name__ == "__main__":
    main()