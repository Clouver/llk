#
# import pyautogui
# import win32gui
#
# def screenshot(window_title=None):
#     if window_title:
#         hwnd = win32gui.FindWindow(None, window_title)
#         if hwnd:
#             win32gui.SetForegroundWindow(hwnd)
#             x, y, x1, y1 = win32gui.GetClientRect(hwnd)
#             x, y = win32gui.ClientToScreen(hwnd, (x, y))
#             x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
#             im = pyautogui.screenshot(region=(x, y, x1, y1))
#             return im
#         else:
#             print('Window not found!')
#     else:
#         im = pyautogui.screenshot()
#         return im
#
#
# im = screenshot("sys_user @taichi_lhb (本机) - 表 - Navicat Premium")
# if im:
#     im.show()
import time

import win32gui
import win32ui
import win32con
import win32api

# grab a handle to the main desktop window
hdesktop = win32gui.GetDesktopWindow()

# determine the size of all monitors in pixels
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

# create a device context
desktop_dc = win32gui.GetWindowDC(hdesktop)
img_dc = win32ui.CreateDCFromHandle(desktop_dc)

# create a memory based device context
mem_dc = img_dc.CreateCompatibleDC()

# create a bitmap object
screenshot = win32ui.CreateBitmap()
screenshot.CreateCompatibleBitmap(img_dc, int(width/2), int(height/2))
mem_dc.SelectObject(screenshot)


while True:
    a = time.time()
    # copy the screen into our memory device context
    mem_dc.BitBlt((0, 0), (int(width/2), int(height/2)), img_dc, (left+200, top+200), win32con.SRCCOPY)
    b = time.time()
    print(b-a)
    # save the bitmap to a file
    screenshot.SaveBitmapFile(mem_dc, 'tmp.bmp')
    x = input()
    if x == 'q':
        break

# free our objects
win32gui.DeleteObject(screenshot.GetHandle())
mem_dc.DeleteDC()
# desktop_dc.DeleteDc()
img_dc.DeleteDC()
win32gui.ReleaseDC(hdesktop, desktop_dc)
