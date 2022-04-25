from map import Map

from config import AREA_RANGE

class FeelArea:
    def __init__(self, map: Map, cx, cy, area=AREA_RANGE) -> None:
        self.map = map
        self.cx = cx
        self.cy = cy
        self.sx = max(cx-area, 0)
        self.sy = max(cy-area, 0)
        self.ex = min(cx+area+1, map.width)
        self.ey = min(cy+area+1, map.height)
        self.area = area

        self.__current_y = self.sy

    def __iter__(self):
        self.__current_y = self.sy
        return self

    def __next__(self):
        if self.__current_y >= self.ey:
            raise StopIteration
        self.__current_y += 1
        return self.map[self.__current_y-1][self.sx:self.ex]