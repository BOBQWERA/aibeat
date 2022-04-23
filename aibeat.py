# utils.py

# 空的迭代器
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from pathlib import Path
import random
import os
if not os.path.exists('aibeat'):
    os.mkdir('aibeat')
os.chdir('./aibeat')

class BadIter:
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

# map.py


BACKGROUND = 0
WALL = 1
CELL1 = 2
CELL2 = 3
ENERGY = 4
CELL1AREA = 5
CELL2AREA = 6

AREA_RANGE = 10

# 地图模型


class Map:
    def __init__(self, width: int, height: int, info: dict, mapsize=10, src=Path('./')) -> None:

        assert isinstance(width, int), ValueError("invalid data type")
        assert isinstance(height, int), ValueError("invalid data type")
        assert isinstance(info, dict), ValueError("invalid data type")

        self.map = [[0 for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height

        self.__iter = 0
        self.__mapsize = mapsize

        for cell in info:
            color = info[cell]['color']
            info[cell]['img'] = Image.new("RGB", (mapsize, mapsize), color)

        self.info = info
        self.img = Image.new(
            "RGB", (self.width*self.mapsize, self.height*self.mapsize), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)

        self.src = src
        self.gene = BadIter()

    def __iter__(self):
        self.gene = map(lambda x: x, self.map)
        return self

    def __next__(self):
        return self.gene.__next__()

    def __getitem__(self, key):
        return self.map[key]

    @property
    def mapsize(self):
        return self.__mapsize

    def data(self):
        return self.map

    def set(self, x, y, cell):
        self.map[y][x] = cell

    def set_wall(self, x, y):
        self.set(x, y, WALL)

    def build_ver_wall(self, hor, ver):
        for v in ver:
            self.set_wall(hor, v)

    def build_hor_wall(self, hor, ver):
        for h in hor:
            self.set_wall(h, ver)

    def build_wall(self, hor, ver):
        if isinstance(hor, int):
            self.build_ver_wall(hor, ver)
        elif isinstance(ver, int):
            self.build_hor_wall(hor, ver)
        else:
            raise

    def build_square(self):
        self.build_wall(0, range(self.height))
        self.build_wall(range(self.width), 0)
        self.build_wall(self.width-1, range(self.height))
        self.build_wall(range(self.width), self.height-1)

    def save(self, name=None):
        for rdx, row in enumerate(self.map):
            for cdx, cal in enumerate(row):
                self.img.paste(self.info[cal]['img'],
                               (cdx*self.mapsize, rdx*self.mapsize))
        if not name:
            name = self.__iter
            self.__iter += 1
        for w in range(1, self.width):
            self.draw.line((w*self.mapsize, 0, w*self.mapsize,
                           self.height*self.mapsize), fill=0, width=1)
        for h in range(1, self.height):
            self.draw.line((0, h*self.mapsize, self.width *
                           self.mapsize, h*self.mapsize), fill=0, width=1)

        self.img.save(self.src / f"{name}.png")


    def render(self, name=None):
        # for rdx, row in enumerate(self.map):
        #     for cdx, cal in enumerate(row):
        #         self.img.paste(self.info[cal]['img'],
        #                         (cdx*self.mapsize, rdx*self.mapsize))
        # if not name:
        #     name = self.__iter
        #     self.__iter += 1
        # for w in range(1, self.width):
        #     self.draw.line((w*self.mapsize, 0, w*self.mapsize,
        #                    self.height*self.mapsize), fill=0, width=1)
        # for h in range(1, self.height):
        #     self.draw.line((0, h*self.mapsize, self.width *
        #                    self.mapsize, h*self.mapsize), fill=0, width=1)
        
        # self.img.show()

        color1=(1,1,1)
        color2=(247/255,220/255,111/255)
        
        mat=[[(0,0,0) for _ in range(self.height) ] for _ in range(self.width) ]
        for rdx, row in enumerate(self.map):
            for cdx, cal in enumerate(row):
                mat[rdx][cdx]= self.info[cal]['color']
        
        plt.clf()  # 清除之前画的图
        cs=plt.imshow(mat)
        
        #plt.xticks(np.linspace(0,8,8,endpoint=False),('a','b','c','d','e','f','g','h'),fontsize=20)
        #plt.yticks(np.linspace(0,8,8,endpoint=False),('1','2','3','4','5','6','7','8'),fontsize=20)
        plt.tick_params(bottom=False,left=False,labeltop=True,labelright=True)
        plt.pause(0.001)  # 暂停一段时间，不然画的太快会卡住显示不出来
        plt.ioff()  # 关闭画图窗口

class MapMixin:
    def __init__(self,map:Map) -> None:
        self.map = map

    def can_move(self,x,y):
        return self.map[y][x] == 0
    def can_put(self,x,y):
        return self.map[y][x] == 0
    def is_energy(self,x,y):
        return self.map[y][x] == ENERGY

    def check_full(self,focus):
        for rdx,r in enumerate(self.map):
            for cdx,c in enumerate(r):
                if c in focus:
                    return False,(cdx,rdx)
        return True,(None,None)

    def select_block(self, focus=BACKGROUND):
        if isinstance(focus,int):
            focus = [focus,]
        width,height = self.map.width,self.map.height
        count = 0
        while True:
            x = random.randint(0,width-1)
            y = random.randint(0,height-1)
            if self.map[y][x] in focus:
                return (x,y)
            if count>1000:
                res,(x,y) = self.check_full(focus)
                if res:
                    return None,None
            if count>5000:
                res,(x,y) = self.check_full(focus)
                return (x,y)


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

class Manager(MapMixin):
    operators = [
        "wait",
        "run",
        "get",
        "put"
    ]
    vector = {
        'up':[0,-1],
        'down':[0,+1],
        'left':[-1,0],
        'right':[+1,0],
    }
    def __init__(self, map: Map, env:Environment) -> None:
        self.map = map
        self.env = env
        self.cells = []

    def gene_cell(self,CellType,cell_id):
        x,y = self.select_block()
        if x==None and y==None:
            raise
        self.map.set(x,y,cell_id)
        self.cells.append(CellType(x,y,cell_id,(self.map.width,self.map.height)))

    def check_border(self,cell,dx,dy):
        if cell.x+dx>=self.map.width or cell.x+dx<0:
            return False
        if cell.y+dy>=self.map.width or cell.x+dx<0:
            return False
        
        return True

    def update(self):
        self.env.update()
        for cell in self.cells:
            feelarea = FeelArea(self.map,cell.x,cell.y)
            op,*args = cell.update(feelarea)
            print(op,args)
            if op not in self.operators:
                raise
            if op == "wait":
                continue
            elif op == "run":
                direct = args[0]
                if direct not in ['up','down','left','right']:
                    raise
                dx,dy = self.vector[direct]
                print('============')
                if not self.check_border(cell,dx,dy):
                    continue
                if not self.can_move(cell.x+dx,cell.y+dy):
                    continue
                print("----------------")
                self.map.set(cell.x,cell.y,BACKGROUND)
                cell.x += dx
                cell.y += dy
                self.map.set(cell.x,cell.y,cell.cell_id)
            elif op == "get":
                direct = args[0]
                if direct not in ['up','down','left','right']:
                    raise
                dx,dy = self.vector[direct]
                if not self.check_border(cell,dx,dy):
                    continue
                if not self.is_energy(cell.x+dx,cell.y+dy):
                    continue
                self.map.set(cell.x+dx,cell.y+dy,BACKGROUND)
                cell.energy += 1
                print('yyyyyyyyyyyyyyyyyyyy')
            elif op == "put":
                direct = args[0]
                if direct not in ['up','down','left','right']:
                    raise
                dx,dy = self.vector[direct]
                if not self.check_border(cell,dx,dy):
                    continue
                if not self.can_put(cell.x+dx,cell.y+dy):
                    continue
                if cell.energy==0:
                    continue
                self.map.set(cell.x+dx,cell.y+dy,cell.cell_id)
                cell.energy-=1
                print('nnnnnnnnnnnnnnnnnnnnnnnnnn')
        # self.map.save()
        self.map.render()









class BaseCell:
    def __init__(self,x,y,cell_id,size) -> None:
        self.x = x
        self.y = y
        self.feelarea = None
        self.energy = 0
        self.cell_id = cell_id
        self.size = size

    def update(self,feelarea):
        return 'wait',None


class TestCell(BaseCell):
    def __init__(self, x, y, cell_id, size) -> None:
        super().__init__(x, y, cell_id, size)
        self.cache = None
    def update(self, feelarea):
        if self.cache:
            cache = self.cache
            self.cache = None
            return cache
        cx = min(self.x,AREA_RANGE)
        cy = min(self.y,AREA_RANGE)
        tx,ty = None,None
        min_dice = None
        for ldx,line in enumerate(feelarea):
            for idx,item in enumerate(line):
                if item == ENERGY:
                    _tx,_ty = idx,ldx
                    dice = (cx-_tx)**2+(cy-_ty)**2
                    if not min_dice or min_dice>dice:
                        min_dice = dice
                        tx,ty = _tx,_ty
        if not tx and not ty:
            direct = random.choice(['up','down','left','right'])
            return 'run',direct,'random'
        if min_dice == 1:
            if tx>cx:
                self.cache = 'put','right'
                return 'get','right'
            elif tx<cx:
                self.cache = 'put','left'
                return 'get','left'
            elif ty>cy:
                self.cache = 'put','down'
                return 'get','down'
            elif ty<cy:
                self.cache = 'put','up'
                return 'get','up'
        if tx>cx:
            return 'run','right','near',min_dice
        elif tx<cx:
            return 'run','left','near',min_dice
        elif ty>cy:
            return 'run','down','near',min_dice
        elif ty<cy:
            return 'run','up','near',min_dice
        direct = random.choice(['up','down','left','right'])
        return 'run',direct,'random'


class Test2Cell(BaseCell):
    def __init__(self, x, y, cell_id, size) -> None:
        super().__init__(x, y, cell_id, size)
        self.cache = []
    def update(self, feelarea):
        vector = [
            ((1,0),'right'),
            ((-1,0),'left'),
            ((0,1),'down'),
            ((0,-1),'up')
        ]
        if self.cache:
            return 'run',self.cache.pop(0)
        area = list(feelarea)
        cx,cy = min(self.x,AREA_RANGE),min(self.y,AREA_RANGE)
        tx,ty = None,None
        min_dice = None
        for ldx,line in enumerate(area):
            for idx,item in enumerate(line):
                if item == ENERGY:
                    _tx,_ty = idx,ldx
                    dice = (cx-_tx)**2+(cy-_ty)**2
                    if not min_dice or min_dice>dice:
                        min_dice = dice
                        tx,ty = _tx,_ty
        if not tx and not ty:
            direct = random.choice(['up','down','left','right'])
            return 'run',direct,'random'
        if min_dice == 1:
            if tx>cx:
                return 'get','right','min_dice'
            elif tx<cx:
                return 'get','left','min_dice'
            elif ty>cy:
                return 'get','down','min_dice'
            elif ty<cy:
                return 'get','up','min_dice'
        step = [((cx,cy),[]),]
        already = [(cx,cy)]
        while step:
            first,fpath = step.pop(0)
            _x,_y = first
            for v,d in vector:
                __x,__y = _x+v[0],_y+v[1]
                if __x<0 or __x>=len(area[0]) or __y<0 or __y>=len(area):
                    continue
                if (__x,__y) in already:
                    continue
                if area[__y][__x] == ENERGY:
                    direct=fpath.pop(0)
                    self.cache = fpath
                    print("bbbbbbbbbbbbbbbbbbbb",type(fpath))
                    return 'run',direct
                _p = fpath.copy()
                _p.append(d)
                step.append(((__x,__y),_p))
                already.append((__x,__y))


        direct = random.choice(['up','down','left','right'])
        return 'run',direct,'last_random'





        
        
        

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
    })
    m.build_square()
    # m.save()

    # a = FeelArea(m, 13, 13)
    # for i in a:
    #     print(i)
    env = SingleDevEnv(m,ENERGY)
    manager = Manager(m,env)
    # manager.gene_cell(BaseCell,CELL1)
    # manager.gene_cell(BaseCell,CELL2)
    # manager.gene_cell(TestCell,CELL1)
    # manager.gene_cell(TestCell,CELL2)
    manager.gene_cell(Test2Cell,CELL1)
    manager.gene_cell(Test2Cell,CELL2)
    
    for i in range(100):
        manager.update()
    


# class MyList:
#     def __init__(self) -> None:
#         self.l = [
#             [1,2],
#             [2,3]
#         ]
#         self.gene = BadIter()

#     def __iter__(self):
#         # self.gene = map(lambda x:x,self.l)
#         return self

#     def __next__(self):
#         return self.gene.__next__()


# for i in MyList():
#     print(i)
