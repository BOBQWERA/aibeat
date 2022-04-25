from map import Map,MapMixin

import random

class Environment:
    def __init__(self, map: Map) -> None:
        self.map = map
        self.__iter = 0

    def update(self):
        self.__iter += 1
            

class SingleDevEnv(Environment,MapMixin):
    random_rate = 0.35

    def __init__(self, map: Map, flag:int) -> None:
        self.flag = flag
        self.__iter = 0
        super().__init__(map)

    def update(self):
        if random.random()>self.random_rate:
            self.__iter+=1
            return
        x,y = self.select_block()
        if x == None and y == None:
            return
        self.map[y][x] = self.flag