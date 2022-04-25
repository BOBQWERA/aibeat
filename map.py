from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from pathlib import Path
from utils import BadIter
import random

from config import *


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

        self.mat=[[(0,0,0) for _ in range(self.height) ] for _ in range(self.width) ]

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
        
        
        for rdx, row in enumerate(self.map):
            for cdx, cal in enumerate(row):
                self.mat[rdx][cdx]= self.info[cal]['color']
        
        plt.clf()  # 清除之前画的图
        cs=plt.imshow(self.mat)
        
        #plt.xticks(np.linspace(0,8,8,endpoint=False),('a','b','c','d','e','f','g','h'),fontsize=20)
        #plt.yticks(np.linspace(0,8,8,endpoint=False),('1','2','3','4','5','6','7','8'),fontsize=20)
        plt.tick_params(bottom=False,left=False,labeltop=True,labelright=True)
        plt.pause(0.001)  # 暂停一段时间，不然画的太快会卡住显示不出来
        plt.ioff()  # 关闭画图窗口



class MapMixin:
    def __init__(self,map:Map) -> None:
        self.map = map

    def can_move(self,x,y,area_id):
        return self.map[y][x] in [area_id,BACKGROUND]
    def can_put(self,x,y):
        return self.map[y][x] == BACKGROUND
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
            count += 1