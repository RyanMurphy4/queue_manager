import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import numpy as np
import cv2 as cv


class Screencap:
    def __init__(self):
        #Resolution that the window coordinates were located on.
        self.relevant_resolution = (1920, 1080)

        #Top left and bottom right of window that shows players position in queue.
        self.QUEUE_POSITION_TL = (15, 225)
        self.QUEUE_POSITION_BR = (390, 282)

        #Top left and bottom right of window that shows when you're able to travel to destination region.
        self.TRAVEL_POSITION_TL = (10, 1020)
        self.TRAVEL_POSITION_BR = (330, 1065)

        #Initializing variables to store users coordinates.
        self.user_resolution = ""

        #User's top left and bottom right coordinates for queue position.
        self.user_queue_position_TL = ''
        self.user_queue_position_BR = ''

        #User's top left and bottom right coordinate for travel position.
        self.user_travel_position_TL = ''
        self.user_travel_position_BR = ''


    @staticmethod
    def take_screenshot():

        hwnd = win32gui.FindWindow(None, 'War  ')

        if not hwnd:

            print("error")

        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

        saveDC.SelectObject(saveBitMap)

        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'RGBA', 0, 1)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        return im

    #Using the dimensions of the numpy array, returns the user's resolution.
    def get_user_resolution(self):
        screenshot = np.array(self.take_screenshot())
        user_resolution = (len(screenshot[1]), len(screenshot))
        self.user_resolution = user_resolution

    #Using the user's resolution, calculates the new (x,y) coordinates for the top left and bottom right regions of interest.
    def get_user_window_points(self):
        self.user_queue_position_TL = self.get_relevant_coords(self.user_resolution, self.relevant_resolution, self.QUEUE_POSITION_TL)
        self.user_queue_position_BR = self.get_relevant_coords(self.user_resolution, self.relevant_resolution, self.QUEUE_POSITION_BR)

        self.user_travel_position_TL = self.get_relevant_coords(self.user_resolution, self.relevant_resolution, self.TRAVEL_POSITION_TL)
        self.user_travel_position_BR = self.get_relevant_coords(self.user_resolution, self.relevant_resolution, self.TRAVEL_POSITION_BR)

    def update_res_and_window_points(self):
        self.get_user_resolution()
        self.get_user_window_points()

    #Method to get the relevant coordinates using a different resolution as an input
    def get_relevant_coords(self, user_resolution, my_resolution, xy_cords):
        x_key = user_resolution[0] / my_resolution[0]
        y_key = user_resolution[1] / my_resolution[1]
        new_x = int(x_key * xy_cords[0])
        new_y = int(y_key * xy_cords[1])
        return new_x, new_y

    #Returns two cropped images of regions of interest.
    def get_two_cropped_img(self):
        screenshot = np.array(self.take_screenshot())
        queue_position = screenshot[self.user_queue_position_TL[1]:self.user_queue_position_BR[1], self.user_queue_position_TL[0]:self.user_queue_position_BR[0]]
        travel_position = screenshot[self.user_travel_position_TL[1]:self.user_travel_position_BR[1],self.user_queue_position_TL[0]:self.user_queue_position_BR[0]]
        return queue_position, travel_position

    #Results are worse, detecting text on the raw image is more accurate.
    def strip_color(self):
        queue_position, travel_position = self.get_two_cropped_img()
        queue_position = cv.cvtColor(queue_position, cv.COLOR_RGB2GRAY)
        travel_position = cv.cvtColor(travel_position, cv.COLOR_RGB2GRAY)
        (_, queue_bw) = cv.threshold(queue_position, 127, 225, cv.THRESH_BINARY)
        (__, travel_bw) = cv.threshold(travel_position, 127, 225, cv.THRESH_BINARY)
        return queue_bw, travel_bw


