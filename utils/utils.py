import ctypes
from ctypes import wintypes
from ctypes.wintypes import HWND, DWORD, RECT

from time import sleep

import numpy as np
import win32api
from PIL import ImageGrab
import win32gui
import win32ui
import win32con
import win32com.client
from PIL import Image
import cv2
import matplotlib.pyplot as plt

DEBUG = False


def cvToPIL(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def PILTocv(img):
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def setForeground(hwnd):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)

def findHwndWithClassName(className):
    return win32gui.FindWindow(className, None)

def getClassName(name):
    hwnd = win32gui.FindWindow(None, name)
    return win32gui.GetClassName(hwnd)

def showWindows():
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)
    # print(winlist)

def cropTableFromImg(img, table_rows=10, table_cols=10):
    left = top = 0
    right = img.width
    bot = img.height

    bSz = ( int((right-left)*1.0/table_cols),int((bot-top)*1.0/table_rows))
    table = []
    for i in range(table_rows):
        table.append([])
        for j in range(table_cols):
            box = (bSz[0]*j, bSz[1]*i, bSz[0]*(j+1), bSz[1]*(i+1))
            table[i].append( np.array(img.crop(box).resize(bSz)) )
     # Image.fromarray(table[0][1]).show()
    # Image.fromarray(table[1][1]).show()
    # Image.fromarray(table[7][3]).show()
    return table

class ScreenShoter:
    def __init__(self):

        # 指定的区域，不指定则截全屏
        self.width = None
        self.height = None
        self.left = None
        self.top = None

        # pywin32 相关结构
        self.hdesktop = win32gui.GetDesktopWindow()
        self.desktop_dc = None
        self.img_dc = None
        self.mem_dc = None
        self.screenshot = None

        self.setDstAttr()

    # 设置局部区域，否则截取全图
    def setDstAttr(self, dst_pos=None):
        self.release()
        if DEBUG:
            print(dst_pos)

        if dst_pos is None:
            # determine the size of all monitors in pixels
            self.width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            self.height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            self.left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            self.top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        else:
            left, top, right, bot = dst_pos
            self.width = right - left
            self.height = bot - top
            self.left = left
            self.top = top

        # create a device context
        self.desktop_dc = win32gui.GetWindowDC(self.hdesktop)
        self.img_dc = win32ui.CreateDCFromHandle(self.desktop_dc)

        # create a memory based device context
        self.mem_dc = self.img_dc.CreateCompatibleDC()

        # create a bitmap object
        self.screenshot = win32ui.CreateBitmap()
        self.screenshot.CreateCompatibleBitmap(self.img_dc, self.width, self.height)
        self.mem_dc.SelectObject(self.screenshot)

    # 截图
    def get_screenshot(self, show=False):

        # copy the screen into our memory device context
        self.mem_dc.BitBlt((0, 0), (self.width, self.height), self.img_dc, (self.left, self.top), win32con.SRCCOPY)

        # save the bitmap to a file
        # screenshot.SaveBitmapFile(mem_dc, 'tmp.bmp')

        bmpinfo = self.screenshot.GetInfo()
        bmpstr = self.screenshot.GetBitmapBits(True)
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        if show:
            im.show()

        return im

    # 释放资源
    def release(self):
        # free our objects
        if self.screenshot:
            win32gui.DeleteObject(self.screenshot.GetHandle())
        if self.mem_dc:
            self.mem_dc.DeleteDC()
        # desktop_dc.DeleteDc()
        if self.img_dc:
            self.img_dc.DeleteDC()
        if self.hdesktop and self.desktop_dc:
            win32gui.ReleaseDC(self.hdesktop, self.desktop_dc)

# 从 img 上的 dots 中取色，并且去重
def getColorFromImg(img, dots):
    pixels = img.load()
    colors = []
    for dot in dots:
        colors.append(pixels[dot[0], dot[1]])
    return set(colors)

# 计算特征 [ [f01, f02, f03 ], [f11, f12, f13], ...]
def descriptBlock(img):

    FEATURE_RATIO = 0.8
    left = int((1-FEATURE_RATIO)/2*img.shape[1])
    top = int((1-FEATURE_RATIO)/2*img.shape[0])
    right = left + int(FEATURE_RATIO*img.shape[1])
    bot = top + int(FEATURE_RATIO*img.shape[0])

    # print((left,top, right,bot))
    # print(img.shape)
    # Image.fromarray( img[top:bot,left:right, :] ).show()

    arr = img[top:bot,left:right, :]
    description = []

    FEATURE_GAP = 3
    for row in arr:
        for i in range(0, len(row), FEATURE_GAP):
            description.append(row[i])

    return description

# descriptBlock 得到的特征进行比较
def isDescriptionSame(a, b):
    # print(a)
    # print(b)

    DESCRIPTION_SAME_GAP = 500000

    D2 = 0
    for i in range(len(a)):
        for j in range(3): # RGB
            D2 += abs(int(a[i][j])-int(b[i][j]))*abs(int(a[i][j])-int(b[i][j]))

    if DEBUG:
        print(D2)
    return DESCRIPTION_SAME_GAP > D2

def isBackground(bgColors, features):
    # print(bgColors)
    # print(block)
    for color in bgColors:
        D2 = 0
        for dot in features:
            for i in range(3):
                D2 += (int(dot[i])-int(color[i]))*(int(dot[i])-int(color[i]))

        if DEBUG:
            print("bg D2: "+str(D2))
        if D2 <= 2000000:
            return True
    return False

if __name__ == '__main__':
    # showWindows()
    # w = WindowCapture()

    # docx 2820814
    # xls 2690768
    # a = win32gui.GetClassName(2952212)SunAwtFrame
    # print(a)

    showWindows()

    a = ScreenShoter()
    a.setDstAttr([52, 548, 295, 725])
    img = a.get_screenshot()

    table = cropTableFromImg(img, [52, 548, 295, 725], 6, 8)

    table[2][2].show()


    #
    # # # while True:
    # img = win32Capture(findHwndWithClassName("Chrome_WidgetWin_1"))

