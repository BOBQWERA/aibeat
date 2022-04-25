from config import *
from map import Map, MapMixin
from feelarea import FeelArea
from env import Environment, SingleDevEnv
from cell import *


class Manager(MapMixin):
    operators = [
        "wait",
        "run",
        "get",
        "put"
    ]
    vector = {
        'up': [0, -1],
        'down': [0, +1],
        'left': [-1, 0],
        'right': [+1, 0],
    }

    def __init__(self, map: Map, env: Environment) -> None:
        self.map = map
        self.env = env
        self.cerner = [
            (1, 1),
            (self.map.width-2, self.map.height-2),
            (1, self.map.height-2),
            (self.map.width-2, 1)
        ]
        self.cells = []
        self.cover = {}

    def gene_cell(self, CellType, cell_id, area_id):
        x, y = self.select_block()
        if x == None and y == None:
            raise
        while (x, y) in self.cerner:
            x, y = self.select_block()
        self.map.set(x, y, cell_id)
        cerner = self.cerner[len(self.cells)]
        self.map.set(cerner[0],cerner[1],area_id)
        self.cells.append(CellType(x, y, cell_id, area_id,
                          (self.map.width, self.map.height)))
        self.cover[(x, y)] = 0

    def check_border(self, cell, dx, dy):
        if cell.x+dx >= self.map.width or cell.x+dx < 0:
            return False
        if cell.y+dy >= self.map.width or cell.x+dx < 0:
            return False

        return True

    def get_score(self):
        self.score = [0 for _ in range(len(self.cells))]
        d = {}
        for idx,cell in enumerate(self.cells):
            d[cell.area_id] = idx
        for line in self.map:
            for item in line:
                if item in d:
                    self.score[d[item]]+=1
        print(self.score)

    def try_finish(self):
        for cell in self.cells:
            if cell.is_alive:
                return
        self.get_score()
        exit()

    def update(self):
        self.env.update()
        for cell in self.cells:
            cell.loss()
            if not cell.is_alive:
                self.try_finish()
            feelarea = FeelArea(self.map, cell.x, cell.y)
            op, *args = cell.update(feelarea)
            if op not in self.operators:
                raise
            if op == "wait":
                continue
            elif op == "run":
                direct = args[0]
                if direct not in ['up', 'down', 'left', 'right']:
                    raise
                dx, dy = self.vector[direct]
                if not self.check_border(cell, dx, dy):
                    continue
                if not self.can_move(cell.x+dx, cell.y+dy, cell.area_id):
                    continue
                self.map.set(cell.x, cell.y, self.cover[(cell.x, cell.y)])
                cell.x += dx
                cell.y += dy
                self.cover[(cell.x, cell.y)] = self.map[cell.y][cell.x]
                self.map.set(cell.x, cell.y, cell.cell_id)

            elif op == "get":
                direct = args[0]
                if direct not in ['up', 'down', 'left', 'right']:
                    raise
                dx, dy = self.vector[direct]
                if not self.check_border(cell, dx, dy):
                    continue
                if not self.is_energy(cell.x+dx, cell.y+dy):
                    continue
                self.map.set(cell.x+dx, cell.y+dy, BACKGROUND)
                cell.energy += 1
            elif op == "put":
                direct = args[0]
                if direct not in ['up', 'down', 'left', 'right']:
                    raise
                dx, dy = self.vector[direct]
                if not self.check_border(cell, dx, dy):
                    continue
                if not self.can_put(cell.x+dx, cell.y+dy):
                    continue
                if cell.energy == 0:
                    continue
                self.map.set(cell.x+dx, cell.y+dy, cell.area_id)
                cell.energy -= 1
                cell.hp += 100
        # self.map.save()
        self.map.render()


if __name__ == "__main__":
    m = Map(50, 50, {
        BACKGROUND: {
            "name": "背景",
            "color": (149, 165, 166),
        },
        WALL: {
            "name": "墙",
            "color": (45, 52, 54),
        },
        CELL1: {
            "name": "细胞1",
            "color": (116, 185, 255),
        },
        CELL2: {
            "name": "细胞2",
            "color": (255, 118, 117),
        },
        CELL3: {
            "name": "细胞3",
            "color": (254, 202, 87),
        },
        CELL4: {
            "name": "细胞4",
            "color": (29, 209, 161),
        },
        ENERGY: {
            "name": "能量",
            "color": (85, 239, 196),
        },
        CELL1AREA: {
            "name": "细胞1区域",
            "color": (9, 132, 227),
        },
        CELL2AREA: {
            "name": "细胞2区域",
            "color": (214, 48, 49),
        },
        CELL3AREA: {
            "name": "细胞3区域",
            "color": (255, 159, 67),
        },
        CELL4AREA: {
            "name": "细胞4区域",
            "color": (16, 172, 132),
        },
    })
    m.build_square()
    # m.save()

    # a = FeelArea(m, 13, 13)
    # for i in a:
    #     print(i)
    env = SingleDevEnv(m, ENERGY)
    manager = Manager(m, env)
    manager.gene_cell(Test5Cell, CELL2, CELL2AREA)
    manager.gene_cell(Test5Cell, CELL1, CELL1AREA)
    manager.gene_cell(Test5Cell, CELL3, CELL3AREA)
    manager.gene_cell(Test5Cell, CELL4, CELL4AREA)

    for i in range(10000):
        if i%1000==0:
            manager.get_score()
        manager.update()
