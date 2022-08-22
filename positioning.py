
# variables
import cv2

from utils.utils import getClassName, PILTocv, ScreenShoter

DEBUG = False


def draw_reactangle_with_drag(event, x, y, flags, param):
    global ix, iy, drawing, img_tmp, img_source, tableRect
    if event == cv2.EVENT_LBUTTONDOWN:
        img_tmp = img_source.copy()
        drawing = True
        ix = x
        iy = y
        tableRect[0] = ix
        tableRect[1] = iy

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img_tmp = img_source.copy()
            cv2.rectangle(img_tmp, pt1=(ix, iy), pt2=(x, y), color=(0, 255, 255), thickness=1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img_tmp, pt1=(ix, iy), pt2=(x, y), color=(0, 255, 255), thickness=1)
        tableRect[2] = x
        tableRect[3] = y


def dotting_recall(event, x, y, flags, param):
    global ix, iy, img_tmp, img_source, dots
    if event == cv2.EVENT_LBUTTONDOWN:
        dots.append((x,y))
        img_tmp = img_source.copy()
        for dot in dots:
            cv2.circle(img_tmp, dot, 5, (255,255,255), 2)
            cv2.circle(img_tmp, dot, 2, (0, 0, 0), 2)

def dottingBackground(img):
    global img_source, img_tmp
    img_source = PILTocv(img)
    img_tmp = img_source.copy()

    cv2.namedWindow(winname="dotting background")
    cv2.setMouseCallback("dotting background", dotting_recall)

    while True:
        cv2.imshow("dotting background", img_tmp)
        ch = cv2.waitKey(10)
        if ch == 13:
            break
        elif ch == 8 and dots: # backspace
            dots.pop()
            img_tmp = img_source.copy()
            for dot in dots:
                cv2.circle(img_tmp, dot, 5, (255, 255, 255), 2)
                cv2.circle(img_tmp, dot, 2, (0, 0, 0), 2)

    if DEBUG:
        print(dots)
    cv2.destroyAllWindows()

def positioningTable(img):

    global img_source, img_tmp
    img_source = PILTocv(img)
    img_tmp = img_source.copy()

    cv2.namedWindow(winname="positioning")
    cv2.setMouseCallback("positioning", draw_reactangle_with_drag)

    while True:
        cv2.imshow("positioning", img_tmp)
        if cv2.waitKey(10) == 13:
            break
    cv2.destroyAllWindows()

# global var
ix = -1
iy = -1
drawing = False
tableRect = [None, None, None, None]
img_source = None
img_tmp = None
dots = []

if __name__ == '__main__':
    # global var
    ix = -1
    iy = -1
    drawing = False
    tableRect = [None, None, None, None]
    img_source = None
    img_tmp = None
    dots = []
    # screenshot
    a = ScreenShoter()
    a.setDstAttr([52, 548, 295, 725])
    img = a.get_screenshot()

    # run
    # positioningTable(img)
    dottingBackground(img)

    print(tableRect)
