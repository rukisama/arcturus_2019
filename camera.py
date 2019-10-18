from typing import Tuple, Union


class Camera:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x2 = self.x + self.width
        self.y2 = self.y + self.height

    def move_camera(self, target_x: int, target_y: int, map_width: int, map_height: int) -> None:
        x = target_x - self.width // 2
        y = target_y - self.height // 2

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > map_width - self.width - 1:
            x = map_width - self.width - 1
        if y > map_height - self.height - 1:
            y = map_height - self.height - 1

        self.x = x
        self.y = y
        self.x2 = self.x + self.width
        self.y2 = self.y + self.height

    def to_camera_coordinates(self, x: int, y: int) -> Tuple[Union[int, None], Union[int, None]]:
        x, y = x - self.x, y - self.y

        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None, None

        return x, y
