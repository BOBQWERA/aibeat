from config import *

import random

class BaseCell:
    def __init__(self,x,y,cell_id,area_id,size) -> None:
        self.x = x
        self.y = y
        self.feelarea = None
        self.energy = 0
        self.cell_id = cell_id
        self.size = size
        self.area_id = area_id
        self.hp = 1000

    def loss(self):
        self.hp -= 1

    @property
    def is_alive(self):
        return self.hp>0

    def update(self,feelarea):
        return 'wait',None

class greedCell(BaseCell):
    def __init__(self, x, y, cell_id,area_id, size) -> None:
        super().__init__(x, y, cell_id,area_id, size)
        self.bags = 0
        self.bigdict = 0
    
    def getNear(self,feelarea):
        res = list(feelarea)
        cx = min(self.x,AREA_RANGE)
        cy = min(self.y,AREA_RANGE)
        #left
        if(cx-1>0):
            leftElement = res[cy][cx-1]
        else:
            leftElement = WALL
        #up
        if(cy-1>0):
            upElement = res[cy-1][cx]
        else:
            upElement = WALL
        #right
        if(cx+1<len(res)):
            rightElement = res[cy][cx+1]
        else:
            rightElement = WALL
        #down
        if(cy+1<len(res[0])):
            downElement = res[cy+1][cx]
        else:
            downElement = WALL

        return (upElement,downElement,leftElement,rightElement)



    def update(self, feelarea):
        directs = ['up','down','left','right']
        obdir = [1,0,3,2]
        near = self.getNear(feelarea)
        #print(near)
        for index,element in enumerate(near):
            if element == ENERGY:
                print("存在",index)
                self.bags += 1
                return 'get',directs[index]
        
        if(near[self.bigdict]==BACKGROUND):
            if self.bags:
                #print("存在",self.bags)
                if near[obdir[self.bigdict]]==BACKGROUND:
                    self.bags -= 1
                    return 'put',directs[obdir[self.bigdict]]
            return 'run',directs[self.bigdict]
        
        dir = self.bigdict
        if dir == 0 or dir == 1:
            while dir == self.bigdict:
                dir = random.choice([2,3])
        else:
            while dir == self.bigdict:
                dir = random.choice([0,1])
        self.bigdict = dir
        print(dir)
        return 'run',directs[self.bigdict]




class TestCell(BaseCell):
    def __init__(self, x, y, cell_id,area_id, size) -> None:
        super().__init__(x, y, cell_id,area_id, size)
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
    def __init__(self, x, y, cell_id,area_id, size) -> None:
        super().__init__(x, y, cell_id,area_id, size)
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
                    # print("bbbbbbbbbbbbbbbbbbbb",type(fpath))
                    return 'run',direct
                _p = fpath.copy()
                _p.append(d)
                step.append(((__x,__y),_p))
                already.append((__x,__y))


        direct = random.choice(['up','down','left','right'])
        return 'run',direct,'last_random'


class Test3Cell(BaseCell):
    def __init__(self, x, y, cell_id,area_id, size) -> None:
        super().__init__(x, y, cell_id,area_id, size)
        self.cache = []
    def update(self, feelarea):
        if self.energy>0:
            direct = random.choice(['up','down','left','right'])
            return 'put',direct
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
                    # print("bbbbbbbbbbbbbbbbbbbb",type(fpath))
                    return 'run',direct
                if area[__y][__x] not in [BACKGROUND,self.area_id]:
                    continue
                _p = fpath.copy()
                _p.append(d)
                step.append(((__x,__y),_p))
                already.append((__x,__y))


        direct = random.choice(['up','down','left','right'])
        return 'run',direct,'last_random'


class Test4Cell(BaseCell):
    def __init__(self, x, y, cell_id,area_id, size) -> None:
        super().__init__(x, y, cell_id,area_id, size)
        self.cache = []

    def near_block(self,x,y,area,flag):
        if area[y][x] != BACKGROUND:
            return False
        if x>0 and area[y][x-1] == flag:
            return True
        if x<len(area[0])-1 and area[y][x+1]==flag:
            return True
        if y>0 and area[y-1][x] == flag:
            return True
        if y<len(area)-1 and area[y+1][x]==flag:
            return True
        return False

    def update(self, feelarea):
        cx,cy = min(self.x,AREA_RANGE),min(self.y,AREA_RANGE)
        area = list(feelarea)
        if self.energy>0:
            if cx>0 and self.near_block(cx-1,cy,area,self.area_id):
                return 'put','left'
            if cx<len(area[0])-1 and self.near_block(cx+1,cy,area,self.area_id):
                return 'put','right'
            if cy>0 and self.near_block(cx,cy-1,area,self.area_id):
                return 'put','up'
            if cy<len(area)-1 and self.near_block(cx,cy+1,area,self.area_id):
                return 'put','down'
        if self.energy>20 and random.random()>0.05:
            if cx>0 and area[cy][cx-1] == BACKGROUND:
                return 'put','left'
            if cx<len(area[0])-1 and area[cy][cx+1] == BACKGROUND:
                return 'put','right'
            if cy>0 and area[cy-1][cx] == BACKGROUND:
                return 'put','up'
            if cy<len(area)-1 and area[cy+1][cx] == BACKGROUND:
                return 'put','down'
        vector = [
            ((1,0),'right'),
            ((-1,0),'left'),
            ((0,1),'down'),
            ((0,-1),'up')
        ]
        if self.cache:
            return 'run',self.cache.pop(0)
        
        
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
                    # print("bbbbbbbbbbbbbbbbbbbb",type(fpath))
                    return 'run',direct
                if area[__y][__x] not in [BACKGROUND,self.area_id]:
                    continue
                _p = fpath.copy()
                _p.append(d)
                step.append(((__x,__y),_p))
                already.append((__x,__y))


        direct = random.choice(['up','down','left','right'])
        return 'run',direct,'last_random'