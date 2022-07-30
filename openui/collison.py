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

    def collide(self, x: float, y: float) -> bool:
        box = self.box
        cx = x >= box.x1 and x <= box.x2
        cy = y >= box.y1 and y <= box.y2

        return cx and cy
