import ctypes
import os
import time
import utilities.random_util as rd
import cv2
import numpy as np
import pyautogui as pag


class RemoteIO:
    """
Key Event arguments  = KeyEvent(PID,ID, When, Modifiers, KeyCode, KeyChar, KeyLocation);
Mouse Event arguements = MouseEvent(PID,ID, When, Modifiers, X, Y, ClickCount, PopupTrigger, Button);
Mouse Wheel Event arguemnts = MouseWheelEvent(PID,ID, When, Modifiers, X, Y, ClickCount, PopupTrigger, ScrollType, ScrollAmount, WheelRotation);
Focus Event arguments = FocusEvent(PID,ID);

ID's

Key events
    KEY_TYPED = 400,
    KEY_PRESSED = 401,
    KEY_RELEASED = 402
    
Mouse Events
    NOBUTTON = 0,
    BUTTON1 = 1, #left click
    BUTTON2 = 2, #mouse wheel
    BUTTON3 = 3, #right click
    MOUSE_CLICK = 500,
    MOUSE_PRESS = 501,
    MOUSE_RELEASE = 502,
    MOUSE_MOVE = 503,
    MOUSE_ENTER = 504,
    MOUSE_EXIT = 505,
    MOUSE_DRAG = 506,
    MOUSE_WHEEL = 507
    
Focus Events
    GAINED = 1004,
    LOST = 1005
 
    """

    def __init__(self, PID):
        self.PID = PID
        self.folder_name = "Plugins"
        self.folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.folder_name)
        self.kinput_path = os.path.join(self.folder_path, "KInputCtrl.dll")
        self.kinput = ctypes.cdll.LoadLibrary(self.kinput_path)
        self.CurX = 0
        self.CurY = 0
        
        self.kinput.KInput_Create.argtypes = [ctypes.c_uint32]
        self.kinput.KInput_Create.restype = ctypes.c_bool
        self.kinput.KInput_Delete.argtypes = [ctypes.c_uint32]
        self.kinput.KInput_Delete.restype = ctypes.c_bool
        self.kinput.KInput_FocusEvent.argtypes = [ctypes.c_uint32, ctypes.c_int]
        self.kinput.KInput_FocusEvent.restype = ctypes.c_bool
        self.kinput.KInput_KeyEvent.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_ulonglong, ctypes.c_int, ctypes.c_int, ctypes.c_ushort, ctypes.c_int]
        self.kinput.KInput_KeyEvent.restype = ctypes.c_bool
        self.kinput.KInput_MouseEvent.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_ulonglong, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_int]
        self.kinput.KInput_MouseEvent.restype = ctypes.c_bool
        self.kinput.KInput_MouseWheelEvent.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_ulonglong, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.kinput.KInput_MouseWheelEvent.restype = ctypes.c_bool
        self.kinput.KInput_Create(self.PID)

    @staticmethod
    def current_time_millis():
        return int(round(time.time() * 1000))

    def click(self, x, y):
        #Mouse Event arguements = MouseEvent(PID,ID, When, Modifiers, X, Y, ClickCount, PopupTrigger, Button);
        LOWER_BOUND_CLICK = 0.03  # Milliseconds
        UPPER_BOUND_CLICK = 0.2  # Milliseconds
        AVERAGE_CLICK = 0.06  # Milliseconds
        
        self.kinput.KInput_FocusEvent(self.PID, 1004)
        self.kinput.KInput_MouseEvent(self.PID, 501, self.current_time_millis(), 1, x, y, 1, False, 1)#mouse Press
        time.sleep(rd.truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        self.kinput.KInput_MouseEvent(self.PID, 502, self.current_time_millis(), 1, x, y, 1, False, 1)#mouse Release  
        
    def Right_click(self, x, y):
        #Mouse Event arguements = MouseEvent(ID, When, Modifiers, X, Y, ClickCount, PopupTrigger, Button);
        LOWER_BOUND_CLICK = 0.03  # Milliseconds
        UPPER_BOUND_CLICK = 0.2  # Milliseconds
        AVERAGE_CLICK = 0.06  # Milliseconds
        self.kinput.KInput_FocusEvent(self.PID, 1004)
        self.kinput.KInput_MouseEvent(self.PID, 501, self.current_time_millis(), 0, x, y, 1, False, 3)#mouse Press
        time.sleep(rd.truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        self.kinput.KInput_MouseEvent(self.PID, 502, self.current_time_millis(), 0, x, y, 1, False, 3)#mouse Release
        
    def Mouse_move(self,x,y): 
        self.kinput.KInput_FocusEvent(self.PID, 1004)
        self.kinput.KInput_MouseEvent(self.PID, 504, self.current_time_millis(), 0, x, y, 0, False, 0) # MOUSE_ENTER
        self.kinput.KInput_MouseEvent(self.PID, 503, self.current_time_millis(), 0, x, y, 0, False, 0) # MOUSE_MOVE
        self.CurX = x
        self.CurY = y
        
      
                
        
        
    def send_key_event(self, ID, KeyChar):
        self.kinput.KInput_FocusEvent(self.PID, 1004)
        self.kinput.KInput_KeyEvent(self.PID, ID, self.current_time_millis(), 0, 0, ord(KeyChar),0)
        
    def send_modifier_key(self, ID, key):
        # Set the keyID based on the key argument
        if key == 'shift':
            keyID = 16
        elif key == 'enter':
            keyID = 10
        elif key == 'alt':
            keyID = 18
        else:
            raise ValueError(f"Invalid key: {key}")

        self.kinput.KInput_FocusEvent(self.PID, 1004)
        self.kinput.KInput_KeyEvent(self.PID, ID, self.current_time_millis(), 0, keyID, 0, 0)     
        
    def send_arrow_key(self, ID, key):
        # Set the keyID based on the key argument
        if key == 'left':
            keyID = 37
        elif key == 'right':
            keyID = 39
        elif key == 'up':
            keyID = 38
        elif key == 'down':
            keyID = 40
        else:
            raise ValueError(f"Invalid key: {key}")

        self.kinput.KInput_FocusEvent(self.PID, 1004)
        self.kinput.KInput_KeyEvent(self.PID, ID, self.current_time_millis(), 0, keyID, 0, 0)   
        
    def get_current_position(self):
        return self.CurX, self.CurY
        
    
        
        
#this is test code,
#PID = 29100 #runelite pid goes here
# Create a RemoteIO instance for the target process
#remote_io = RemoteIO(PID)

# Send the key event
#remote_io.send_key_event(400, 'A')
#print("here")

