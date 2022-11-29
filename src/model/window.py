'''
This class contains functions for interacting with the game client window. All Bot classes have a
Window object as a property. This class allows you to locate important points/areas on screen no 
matter where the game client is positioned. This class can be extended to add more functionality
(See RuneLiteWindow within runelite_bot.py for an example). 
'''
from deprecated import deprecated
from typing import List, Union
from utilities.geometry import Rectangle, Point
import pygetwindow
import time
import utilities.bot_cv as bcv

class Window:

    client_fixed: bool = None

    # CP Area
    hp_bar: Rectangle = None
    prayer_bar: Rectangle = None
    control_panel: Rectangle = None  # https://i.imgur.com/BeMFCIe.png
    cp_tabs: List[Rectangle] = None  # https://i.imgur.com/huwNOWa.png
    inventory_slots: List[Rectangle] = None  # https://i.imgur.com/gBwhAwE.png

    # Chat Area
    chat: Rectangle = None  # https://i.imgur.com/u544ouI.png
    chat_tabs: List[Rectangle] = None  # https://i.imgur.com/2DH2SiL.png

    # Minimap Area
    minimap_area: Rectangle = None  # https://i.imgur.com/idfcIPU.png OR https://i.imgur.com/xQ9xg1Z.png
    minimap: Rectangle = None
    compass_orb: Rectangle = None
    hp_orb_text: Rectangle = None
    prayer_orb_text: Rectangle = None
    quick_prayer_orb: Rectangle = None
    run_orb: Rectangle = None
    spec_orb: Rectangle = None

    # Game View Area
    game_view: Rectangle = None

    def __init__(self, window_title: str, padding_top: int, padding_left: int) -> None:
        '''
        Creates a Window object with various methods for interacting with the client window.
        Args:
            window_title: The title of the client window.
            padding_top: The height of the client window's header.
            padding_left: The width of the client window's left border.
        '''
        self.window_title = window_title
        self.padding_top = padding_top
        self.padding_left = padding_left
    
    def _get_window(self):
        self._client = pygetwindow.getWindowsWithTitle(self.window_title)
        if self._client:
            return self._client[0]
        else:
            raise pygetwindow.PyGetWindowException("No client window found.")
    
    window = property(
        fget=_get_window,
        doc="A Win32Window reference to the game client and its properties."
    )

    def focus(self) -> None:
        '''
        Focuses the client window.
        '''
        if client := self.window:
            client.activate()

    def position(self) -> Point:
        '''
        Returns the origin of the client window as a Point.
        '''
        if client := self.window:
            return Point(client.left, client.top)
    
    def rectangle(self) -> Rectangle:
        '''
        Returns a Rectangle outlining the entire client window.
        '''
        if client := self.window:
            return Rectangle(client.left, client.top, client.width, client.height)
    
    def resize(self, width: int, height: int) -> None:
        '''
        Resizes the client window..
        Args:
            width: The width to resize the window to.
            height: The height to resize the window to.
        '''
        if client := self.window:
            client.size = (width, height)
    
    def initialize(self) -> bool:
        '''
        Initializes the client window by locating critical UI regions.
        This function should be called when the bot is started or resumed (done by default).
        Returns:
            True if successful, False otherwise.
        '''
        start_time = time.time()
        client_rect = self.rectangle()
        a = self.__locate_minimap(client_rect)
        b = self.__locate_chat(client_rect)
        c = self.__locate_control_panel(client_rect)
        d = self.__locate_game_view(client_rect)
        if all(a, b, c, d): # if all templates found\
            print(f"Window.initialize() took {time.time() - start_time} seconds.")
            return True
        return False
        
    def __locate_chat(self, client_rect: Rectangle) -> bool:
        '''
        Locates the chat area on the client.
        Args:
            client_rect: The client area to search in.
        Returns:
            True if successful, False otherwise.
        '''
        if chat := bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/chat.png", client_rect):
            # Locate chat tabs
            x, y = 5, 143
            for i in range(7):
                self.chat_tabs[i] = Rectangle(left=x + chat.left, top=y + chat.top, width=52, height=19)
                x += 62  # btn width is 52px, gap between each is 10px
            self.chat = chat
            return True
        print("Window.__locate_chat(): Failed to find chatbox.")
        return False
    
    def __locate_control_panel(self, client_rect: Rectangle) -> bool:
        '''
        Locates the control panel area on the client.
        Args:
            client_rect: The client area to search in.
        Returns:
            True if successful, False otherwise.
        '''
        if cp := bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/inv.png", client_rect):
            self.__locate_inv_slots(cp)
            self.__locate_cp_tabs(cp)
            self.control_panel = cp
            return True
        print("Window.__locate_control_panel(): Failed to find control panel.")
        return False

    def __locate_inv_slots(self, cp: Rectangle) -> None:
        '''
        Creates Rectangles for each inventory slot relative to the control panel, storing it in the class property.
        '''
        slot_w, slot_h = 36, 32  # dimensions of a slot
        gap_x, gap_y = 5, 3  # pixel gap between slots
        i = 0
        y = 44 + cp.top  # start y relative to cp template
        for _ in range(7):
            x = 40 + cp.left  # start x relative to cp template
            for _ in range(4):
                self.inventory_slots[i] = Rectangle(left=x, top=y, width=slot_w, height=slot_h)
                x += slot_w + gap_x
                i += 1
            y += slot_h + gap_y
    
    def __locate_cp_tabs(self, cp: Rectangle) -> None:
        '''
        Creates Rectangles for each inventory slot relative to the control panel, storing it in the class property.
        '''
        slot_w, slot_h = 29, 26  # top row tab dimensions
        gap = 4  # 4px gap between tabs
        y = 4  # 4px from top for first row
        i = 0
        for _ in range(2):
            x = 8 + cp.left
            for _ in range(7):
                self.cp_tabs[i] = Rectangle(left=x, top=y, width=slot_w, height=slot_h)
                x += slot_w + gap
                i += 1
            y = 303  # 303px from top for second row
            slot_h = 28  # slightly taller tab Rectangles for second row

    def __locate_game_view(self, client_rect: Rectangle) -> bool:
        '''
        Locates the game view while considering the client mode (Fixed/Resizable). https://i.imgur.com/uuCQbxp.png
        Args:
            client_rect: The client area to search in.
        Returns:
            True if successful, False otherwise.
        '''
        if self.minimap_area is None or self.chat is None or self.control_panel is None:
            print("Window.__locate_game_view(): Failed to locate game view. Missing minimap, chat, or control panel.")
            return False
        if self.client_fixed:
            # Uses the chatbox and known fixed size of game_view to locate it in fixed mode
            self.game_view = Rectangle(left=self.chat.left, top=self.chat.top - 337, width=517, height=337)
        else:
            # Uses control panel to find right-side bounds of game view in resizable mode
            self.game_view = Rectangle.from_points(Point(client_rect.left + self.padding_left, client_rect.top + self.padding_top),
                                                   self.control_panel.get_bottom_right())
            self.game_view.subtract_list = [self.minimap.to_dict(), self.chat.to_dict(), self.control_panel.to_dict()]
        return True

    def __locate_minimap(self, client_rect: Rectangle) -> bool:
        '''
        Locates the minimap area on the clent window and all of its internal positions.
        Args:
            client_rect: The client area to search in.
        Returns:
            True if successful, False otherwise.
        '''
        # 'm' refers to minimap area
        if m := bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/minimap.png", client_rect):
            self.client_fixed = False
            self.minimap = Rectangle(left=52 + m.left, top=5 + m.top, width=154, height=155)
            self.compass_orb = Rectangle(left=40 + m.left, top=7 + m.top, width=24, height=26)
            self.hp_orb_text = Rectangle(left=4 + m.left, top=55 + m.top, width=20, height=13)
            self.quick_prayer_orb = Rectangle(left=31 + m.left, top=85 + m.top, width=17, height=21)
            self.prayer_orb_text = Rectangle(left=4 + m.left, top=94 + m.top, width=20, height=13)
            self.run_orb = Rectangle(left=40 + m.left, top=119 + m.top, width=17, height=21)
            self.spec_orb = Rectangle(left=62 + m.left, top=144 + m.top, width=18, height=20)
            self.minimap_area = m
            return True
        if m := bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/minimap_fixed.png", client_rect):
            self.client_fixed = True
            self.minimap = Rectangle(left=52 + m.left, top=4 + m.top, width=147, height=160)
            self.compass_orb = Rectangle(left=31 + m.left, top=7 + m.top, width=24, height=25)
            self.hp_orb_text = Rectangle(left=4 + m.left, top=60 + m.top, width=20, height=13)
            self.quick_prayer_orb = Rectangle(left=30 + m.left, top=80 + m.top, width=19, height=20)
            self.prayer_orb_text = Rectangle(left=4 + m.left, top=89 + m.top, width=20, height=13)
            self.run_orb = Rectangle(left=40 + m.left, top=112 + m.top, width=19, height=20)
            self.spec_orb = Rectangle(left=62 + m.left, top=137 + m.top, width=19, height=20)
            self.minimap_area = m
            return True
        print("Window.__locate_minimap(): Failed to find minimap.")
        return False

class MockWindow(Window):
    def __init__(self):
        super().__init__(window_title="None", padding_left=0, padding_top=0)
    
    def _get_window(self):
        print("MockWindow._get_window() called.")
    
    window = property(
        fget=_get_window,
        doc="A Win32Window reference to the game client and its properties."
    )
    
    def initialize(self) -> None:
        print("MockWindow.initialize() called.")
    
    def focus(self) -> None:
        print("MockWindow.focus() called.")

    def position(self) -> Point:
        print("MockWindow.position() called.")
