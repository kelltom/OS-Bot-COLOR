from deprecated import deprecated
from utilities.geometry import Rectangle, Point
import pygetwindow


# TODO: We could implement template matching to make this class functional
#       for all OSRS bots and move it to Bot.py. The only problem is when
#       people want to identify their own custom points - they would have to
#       be aware that you'd have to hardcode the value relative to the game view.
class RuneLiteWindow:           
    def __init__(self, window_title: str) -> None:
        self.window_title = window_title
    
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
    
    def resize(self, width: int = 773, height: int = 534) -> None:
        '''
        Resizes the client window. Default size is 773x534 (minsize of fixed layout).
        Args:
            width: The width to resize the window to.
            height: The height to resize the window to.
        '''
        if client := self.window:
            client.size = (width, height)
    
    def get_relative_point(self, x, y) -> Point:
        '''
        Returns a Point relative to the client window.
        Args:
            x: The x coordinate when client is anchored to top-left of screen.
            y: The y coordinate when client is anchored to top-left of screen.
        Returns:
            A Point relative to the client window.
        '''
        offset = self.position()
        return Point(x + offset.x, y + offset.y)
    
    # === Rectangles ===
    # TODO: Currently only works when client is in fixed layout mode and minsize.
    #       Need to make everything relative to the game view - which requires template matching.
    # The following rects are used to isolate specific areas of the client window.
    # Their positions were identified when game client was in fixed layout & anchored to the screen origin.
    def rect_current_action(self) -> Rectangle:
        '''
        Returns a Rectangle outlining the 'current action' area of the game view.
        E.g., Woodcutting plugin, Opponent Information plugin (<name of NPC>), etc.
        '''
        return Rectangle.from_points(Point(13, 51), Point(140, 73), self.position())
    
    def rect_game_view(self) -> Rectangle:
        '''Returns a Rectangle outlining the game view.'''
        return Rectangle.from_points(Point(8, 50), Point(517, 362), self.position())

    def rect_cp(self) -> Rectangle:
        '''Returns a Rectangle outlining the control panel area.'''
        return Rectangle.from_points(Point(528, 194), Point(763, 526), self.position())
    
    # TODO: Deprecate once RuneLite API has been implemented.
    def rect_hp(self) -> Rectangle:
        '''Returns a Rectangle outlining the text on the HP status bar.'''
        return Rectangle.from_points(Point(528, 81), Point(549, 95), self.position())
    
    def rect_inventory(self) -> Rectangle:
        '''Returns a Rectangle outlining the inventory area.'''
        return Rectangle.from_points(Point(554, 230), Point(737, 491), self.position())
    
    def rect_minimap(self) -> Rectangle:
        '''Returns a Rectangle outlining the minimap area.'''
        return Rectangle.from_points(Point(577, 39), Point(715, 188), self.position())
    
    # TODO: Deprecate once RuneLite API has been implemented.
    def rect_prayer(self) -> Rectangle:
        '''Returns a Rectangle outlining the prayer bar.'''
        return Rectangle.from_points(Point(530, 117), Point(550, 130), self.position())

    # === Points ===
    # --- Orbs ---
    def orb_compass(self) -> Point:
        '''Returns the position of the compass orb as a Point.'''
        return self.get_relative_point(571, 48)
    
    def orb_prayer(self) -> Point:
        '''Returns the position of the prayer orb as a Point.'''
        return self.get_relative_point(565, 119)
    
    def orb_spec(self) -> Point:
        '''Returns the position of the special attack orb as a Point.'''
        return self.get_relative_point(597, 178)

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
