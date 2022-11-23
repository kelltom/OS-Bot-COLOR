'''
This class contains functions for interacting with the game client window. All Bot classes have a
Window object as a property. This class allows you to locate important points/areas on screen no 
matter where the game client is positioned. This class can be extended to add more functionality
(See RuneLiteWindow within runelite_bot.py for an example). 

TODO: Nearly all defined rectangle functions within this class should eventually be converted to 
use template matching instead of hardcoded pixels.
'''
from deprecated import deprecated
from utilities.geometry import Rectangle, Point
import pygetwindow


class Window:     
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
    
    def __get_relative_point(self, x: int, y: int) -> Point:
        '''
        Returns a Point relative to the client window. Do not use this method outside of this class.
        Args:
            x: The x coordinate when client is anchored to top-left of screen, relative to game view.
            y: The y coordinate when client is anchored to top-left of screen, relative to game view.
        Returns:
            A Point relative to the client window.
        '''
        offset = self.position()
        return Point(x + offset.x + self.padding_left, y + offset.y + self.padding_top)
    
    def get_relative_point(self, x: int, y: int) -> Point:
        '''
        Returns a Point relative to the client window.
        Args:
            x: The x coordinate when client is anchored to top-left of screen.
            y: The y coordinate when client is anchored to top-left of screen.
        Returns:
            A Point relative to the client window.
        Example:
            E.g., if I know the position of the Map button is (730, 160) when
            the RuneLite client is anchored to the top-left of the screen, I can use:
                `map_btn = self.get_relative_point(730, 160)`
            in my bot's code to get the position of the Map button no matter
            where the client is on screen. Consider image search as an alternative.
        '''
        offset = self.position()
        return Point(x + offset.x, y + offset.y)
    
    # === Rectangles ===
    # The following rects are used to isolate specific areas of the client window.
    # Their positions are relative to the top-left corner of the GAME VIEW.
    def rect_current_action(self) -> Rectangle:
        '''
        Returns a Rectangle outlining the 'current action' area of the game view.
        E.g., Woodcutting plugin, Opponent Information plugin (<name of NPC>), etc.
        '''
        return Rectangle.from_points(self.__get_relative_point(13, 25),
                                     self.__get_relative_point(140, 47))
    
    def rect_game_view(self) -> Rectangle:
        '''Returns a Rectangle outlining the game view.'''
        return Rectangle.from_points(self.__get_relative_point(8, 24),
                                     self.__get_relative_point(517, 336))

    def rect_cp(self) -> Rectangle:
        '''Returns a Rectangle outlining the control panel area.'''
        return Rectangle.from_points(self.__get_relative_point(528, 168),
                                     self.__get_relative_point(763, 500))
    
    def rect_hp(self) -> Rectangle:
        '''Returns a Rectangle outlining the text on the HP status bar.'''
        return Rectangle.from_points(self.__get_relative_point(528, 55),
                                     self.__get_relative_point(549, 69))
    
    def rect_inventory(self) -> Rectangle:
        '''Returns a Rectangle outlining the inventory area.'''
        return Rectangle.from_points(self.__get_relative_point(554, 204),
                                     self.__get_relative_point(737, 465))
    
    def rect_minimap(self) -> Rectangle:
        '''Returns a Rectangle outlining the minimap area.'''
        return Rectangle.from_points(self.__get_relative_point(577, 13),
                                     self.__get_relative_point(715, 162))
    
    def rect_prayer(self) -> Rectangle:
        '''Returns a Rectangle outlining the prayer bar.'''
        return Rectangle.from_points(self.__get_relative_point(530, 91),
                                     self.__get_relative_point(550, 104))

    # === Points ===
    # --- Orbs ---
    def orb_compass(self) -> Point:
        '''Returns the position of the compass orb as a Point.'''
        return self.__get_relative_point(571, 22)
    
    def orb_prayer(self) -> Point:
        '''Returns the position of the prayer orb as a Point.'''
        return self.__get_relative_point(565, 93)
    
    def orb_spec(self) -> Point:
        '''Returns the position of the special attack orb as a Point.'''
        return self.__get_relative_point(597, 152)

    # --- Control Panel ---
    def cp_tab(self, tab: int) -> Point:
        '''
        Returns the position of a control panel tab as a Point.
        Args:
            tab: The index of the tab to return the position of.
                (top-left tab = 1, bottom-right tab = 14)
        Returns:
            The position of a control panel tab as a Point.
        '''
        if (tab < 1) or (tab > 14):
            raise ValueError("Tab index must be between 1 and 14.")
        cp = self.rect_cp()
        if tab <= 7:
            return Point(x=cp.left + 16 + ((tab - 1) * 33), y=cp.top + 16)
        else:
            return Point(x=cp.left + 16 + ((tab % 8) * 33), y=cp.top + cp.height - 16)

    # --- Inventory ---
    def inventory_slots(self, indices: list[int] = None) -> list[Point]:
        '''
        Fetches the positions of inventory slots as Points.
        Args:
            indices: A list of inventory slot indices to return the positions of (0-27).
                     If None, returns the positions of all inventory slots.
        Returns:
            A list of Points representing the positions of inventory slots.
        '''
        inv = self.rect_inventory()
        res = []
        curr_y = inv.top + 26
        for _ in range(7):
            curr_x = inv.left + 26  # reset x
            for _ in range(4):
                res.append(Point(x=curr_x, y=curr_y))
                curr_x += 42  # x delta
            curr_y += 36  # y delta
        return res if indices is None else [res[i] for i in indices]

class MockWindow(Window):
    def __init__(self):
        super().__init__(window_title="None", padding_left=0, padding_top=0)
    
    def _get_window(self):
        print("MockWindow._get_window() called.")
    
    window = property(
        fget=_get_window,
        doc="A Win32Window reference to the game client and its properties."
    )

    def focus(self) -> None:
        print("MockWindow.focus() called.")

    def position(self) -> Point:
        print("MockWindow.position() called.")