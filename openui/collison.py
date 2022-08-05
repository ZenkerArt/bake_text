from dataclasses import dataclass


@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float


class BoundingBox:
    box: BBox

    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.box = BBox(x1, y1, x2, y2)

    def collide(self, x: float, y: float, add_x: float = 0, add_y: float = 0) -> bool:
        box = self.box
        cx = x >= box.x1 - add_x and x <= box.x2 + add_x
        cy = y >= box.y1 - add_y and y <= box.y2 + add_y

        return cx and cy
