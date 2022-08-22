import os
from time import sleep

# import pythoncom
import pynput.mouse
from PIL import Image

import positioning
from positioning import dottingBackground, positioningTable
from utils.utils import showWindows, ScreenShoter, getColorFromImg, cropTableFromImg, descriptBlock, isDescriptionSame, \
    isBackground
import numpy as np

from pynput.mouse import Button, Controller

from pynput import keyboard

import cv2
# a = win32Capture(4459066)

CFG = {
    "table":{
        "left":0,
        "top":0,
        "right":1920,
        "bottom":1080
    }
}


class Worker():
    def __init__(self):
        self.table = [] # descriptions
        self.f_table = []
        self.bgColor = []

        self.distinctFeatures = []
        self.mappedTable = []

    def mapBlock(self):
        print(len(self.table))
        print(len(self.table[0]))
        self.mappedTable = [ [0]*len(self.table[0]) for i in range(len(self.table)) ]

        for i,col in enumerate(self.f_table):
            for j,feature in enumerate(col):
                toAdd = True
                for k, dFeature in enumerate(self.distinctFeatures):
                    if DEBUG:
                        print(i, j, k)
                    if isBackground(self.bgColor, feature) :
                        self.mappedTable[i][j] = 0
                        toAdd = False
                        break
                    elif isDescriptionSame(dFeature, feature):
                        self.mappedTable[i][j] = k+1
                        toAdd = False
                        break
                if toAdd:
                    self.distinctFeatures.append(feature)
                    self.mappedTable[i][j] = len(self.distinctFeatures)
        while False:
            a = int(input())
            b = int(input())
            c = int(input())
            d = int(input())
            isDescriptionSame(self.distinctFeatures[self.mappedTable[a][b]],
                              self.distinctFeatures[self.mappedTable[c][d]]
                              )
        (print(self.mappedTable))
        pynput.mouse.Events.Scroll
    def searchPair(self):
        for i in range(len(self.table)):
            for j in range(len(self.table[0])):
                continue

    def setAttr(self, colors, table):
        self.setBgcolor(colors)
        self.setTable(table)

    def setTable(self, table):
        self.table = table
        # print(table)
        self.f_table = [ [descriptBlock(block) for block in row] for row in table ]
        # print(self.f_table)
        self.mapBlock()

    def setBgcolor(self, colors):
        self.bgColor =  colors

    def work(self):

        '''
            todo
        
        '''
        def dfs(a, i, j, direction, cnt):
            #print(i, j, a, self.mappedTable[i][j])

            dx = [1, 0, -1, 0]
            dy = [0, 1, 0, -1]
            if cnt>3 or i<0 or i>=len(self.mappedTable) or j<0 or j>=len(self.mappedTable[0]):
                return None

            if a==self.mappedTable[i][j] and cnt!=0:
                return (i,j)
            elif cnt!=0 and self.mappedTable[i][j]!=0: # 不是背景
                return None
            else: # 是背景
                for k in range(4):
                    if abs(k-direction) == 2: # 不能掉头
                        continue
                    elif k==direction:
                        ret = dfs(a, i+dx[k], j+dy[k], k, cnt)    # 同方向
                        if ret is not None:
                            return ret
                    else:
                        ret = dfs(a, i+dx[k], j+dy[k], k, cnt+1)  # 拐角
                        if ret is not None:
                            return ret
                return None


        for i, row in enumerate(self.mappedTable):
            for j, idx in enumerate(row):
                if self.mappedTable[i][j] != 0:
                    # print(i, j)
                    ret = dfs(self.mappedTable[i][j], i, j, -10, 0)
                    #print("ret: ")
                    #print(ret)
                    if ret is not None:
                        return ((i,j), ret)
        return None


class Window():
    def __init__(self):
        self.cfg = CFG
        self.ss = ScreenShoter()
        return

    def setTable(self):

        img = self.ss.get_screenshot()

        # run
        positioningTable(img)

        print(positioning.tableRect)
        self.ss.setDstAttr(positioning.tableRect)

    def setBackgrounds(self):
        # screenshot
        img = self.ss.get_screenshot()

        # run
        dottingBackground(img)

        self.backgroundColors = getColorFromImg(img, positioning.dots)
        print(self.backgroundColors)

    def setRowCol(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def getTable(self):
        img = self.ss.get_screenshot()
        return cropTableFromImg(img, self.rows, self.cols)

    # 用户交互进行设置
    def interactSetting(self):
        win.setTable()
        win.setBackgrounds()
        os.system("cls")
        rows_input = input("rows: ")
        cols_input = input("cols: ")
        print("\n\n\n")
        win.setRowCol( int(rows_input), int(cols_input))



# def on_press(key):
#     '按下按键时执行。'
#     try:
#         print('alphanumeric key {0} pressed'.format(
#             key.char))
#     except AttributeError:
#         print('special key {0} pressed'.format(
#             key))
#     #通过属性判断按键类型。

# 键盘监听回调
def on_release(key):
    global quitCnt, win, worker, clicker
    global toclick1, toclick2, click2ready

    '松开按键时执行。'
    # print('{0} released'.format(
    #     key))
    if key == keyboard.Key.esc:
        quitCnt+=1
        if quitCnt >= 3:
            return False
    else:
        quitCnt = 0

    if key == 'ctrl_r':
        win.interactSetting()
    elif key == keyboard.KeyCode.from_char('e'):
        a = int(input())
        b = int(input())
        c = int(input())
        d = int(input())
        isDescriptionSame(worker.distinctFeatures[worker.mappedTable[a][b]],
                          worker.distinctFeatures[worker.mappedTable[c][d]]
                          )
        isBackground(worker.bgColor,worker.distinctFeatures[worker.mappedTable[a][b]] )
        isBackground(worker.bgColor, worker.distinctFeatures[worker.mappedTable[c][d]])
        tt = win.getTable()
        Image.fromarray(tt[a][b]).show()
        Image.fromarray(tt[c][d]).show()

    elif key == keyboard.KeyCode.from_char('q') and not click2ready:
        # todo click 1
        ret = worker.work()
        if ret is not None:
            toclick1, toclick2 = ret
            worker.mappedTable[toclick1[0]][toclick1[1]] = 0
            for line in worker.mappedTable:
                print(line)
            print("\n")
            clicker.click(toclick1[0], toclick1[1])
            click2ready = True
        else:
            print("None")
        print("1")
    elif key == keyboard.KeyCode.from_char('w') and click2ready:
        # todo click 2
        worker.mappedTable[toclick2[0]][toclick2[1]] = 0
        clicker.click(toclick2[0], toclick2[1])
        click2ready=False
        print("2")
    elif key == keyboard.Key.ctrl_l:
        worker.setAttr( win.backgroundColors, win.getTable())
        print("attr setted, space to work")
        # a,b = worker.work()
    # elif key == keyboard.Key.space:




class Clicker():
    def __init__(self, mouse, tableRect, rows, cols):
        self.mouse = mouse
        self.tableRect = tableRect
        self.sz = [int(tableRect[2]/cols), int(tableRect[3]/rows)]
        self.rows = rows
        self.cols = cols

    def click(self, i, j, sleeptime=0.2):
        # todo
        shift = (self.sz[0]/2, self.sz[1]/2)
        mouse.position = (self.tableRect[0] + shift[0] + self.sz[0]*j,self.tableRect[1] + shift[1] + self.sz[1]*i)

        sleep(sleeptime)

DEBUG = False
if __name__ == "__main__":
    showWindows()

    win = Window()
    # //win.interactSetting()
    # input()
    # qq 连连看的默认参数
    win.ss.setDstAttr([570, 399, 1164, 789])
    win.backgroundColors = {(48, 76, 112)}
    win.setRowCol(11, 19)

    worker = Worker()
    # worker.mappedTable = [
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 2, 9, 2, 6, 0],
    #     [0, 0, 3, 8, 3, 7, 0],
    #     [0, 0, 5, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0]
    # ]

    mouse = Controller()
    # win.ss.width = None
    #         height = None
    #         left = None
    #         top = None
    # win.rows cols
    rct = (win.ss.left, win.ss.top, win.ss.width, win.ss.height)
    clicker = Clicker(mouse, rct, win.rows, win.cols)
    quitCnt = 0

    toclick1 = None
    toclick2 = None
    click2ready = False
    # Collect events until released
    with keyboard.Listener(
            # on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
