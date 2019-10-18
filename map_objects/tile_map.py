import numpy as np
import tcod
from typing import Dict, Union, Tuple
import charmap as ch


map_dtype = np.dtype([("glyph", np.intc), ("fg", "(3,)i4"), ("bg", "(3,)i4")])


class TileMap:
    def __init__(self, width: int, height: int, fg: Tuple[int, int, int] = (255, 0, 0),
                 bg: Tuple[int, int, int] = (128, 0, 0)):
        self.width = width
        self.height = height
        self.tiles: np.ndarray = np.zeros((width, height), dtype=map_dtype, order="F")
        self.glyph: np.ndarray = self.tiles["glyph"]
        self.fg: np.ndarray = self.tiles["fg"]
        self.bg: np.ndarray = self.tiles["bg"]
        self.default_fg = fg
        self.default_bg = bg

        self.glyph[:] = ch.WALL
        self.fg[:] = fg
        self.bg[:] = bg

    def to_json(self) -> Dict:
        json_data = {
            "width": self.width,
            "height": self.height,
            "glyph": self.glyph.tolist(),
            "fg": self.fg.tolist(),
            "bg": self.bg.tolist(),
            "default_fg": self.default_fg,
            "default_bg": self.default_bg
        }

        return json_data

    @staticmethod
    def from_json(json_data: Dict) -> Union["TileMap", None]:
        if json_data is None:
            return None

        width = int(json_data["width"])
        height = int(json_data["height"])
        glyph = np.array(json_data["glyph"])
        fg = np.array(json_data["fg"])
        bg = np.array(json_data["bg"])
        d_fg = json_data["default_fg"]
        d_bg = json_data["default_bg"]

        tile_map = TileMap(width, height, d_fg, d_bg)
        tile_map.tiles["glyph"] = glyph
        tile_map.tiles["fg"] = fg
        tile_map.tiles["bg"] = bg

        return tile_map
