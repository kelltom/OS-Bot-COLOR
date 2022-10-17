'''
The RuneLiteBot class contains properties and functions that are common across all RuneLite-based clients. This class
should be inherited by additional abstract classes representing all bots for a specific game (E.g., Alora, OSRS, etc.).

To determine Thresholds for finding contours: https://pinetools.com/threshold-image
For converting RGB to HSV:
    https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv/48367205#48367205
'''
from abc import ABCMeta
from deprecated import deprecated
from model.bot import Bot, BotStatus
from utilities.bot_cv import Rectangle, Point
from utilities.runelite_cv import Color, isolate_colors
import cv2
import numpy as np
import pyautogui as pag
import pygetwindow
import time
import utilities.bot_cv as bcv
import utilities.runelite_cv as rcv


class RuneLiteBot(Bot, metaclass=ABCMeta):

    # --- Notable Colour Ranges (HSV lower, HSV upper) ---
    TAG_BLUE = Color((90, 100, 255), (100, 255, 255))       # hex: FF00FFFF
    TAG_PURPLE = Color((130, 100, 100), (150, 255, 255))     # hex: FFAA00FF
    TAG_PINK = Color((145, 100, 200), (155, 255, 255))       # hex: FFFF00E7
    TAG_GREEN = Color((40, 100, 255), (70, 255, 255))
    TAG_RED = Color((0, 255, 255), (20, 255, 255))

    # --- Desired client position ---
    # Size and position of the smallest possible fixed OSRS client in top left corner of screen.
    desired_width, desired_height = (773, 534)
    client_window = None  # client region, determined at setup

    # ------- Main Client Rects -------
    rect_current_action = Rectangle(Point(13, 51), Point(140, 73))  # combat/skilling plugin text
    rect_game_view = Rectangle(Point(8, 50), Point(517, 362))  # gameplay area (prev start: x=9, y=31)
    rect_hp = Rectangle(Point(528, 81), Point(549, 95))  # hp number on status bar
    rect_prayer = Rectangle(Point(530, 117), Point(550, 130))  # prayer number on status bar
    rect_inventory = Rectangle(Point(554, 230), Point(737, 491))  # inventory area
    rect_minimap = Rectangle(Point(577, 39), Point(715, 188))  # minimap area

    # ------- Points of Interest -------
    # --- Orbs ---
    orb_compass = Point(x=571, y=48)
    orb_prayer = Point(x=565, y=119)
    orb_spec = Point(x=597, y=178)

    # --- Control Panel (CP) ---
    h1 = 213  # y-axis pixels to top of cp
    h2 = 510  # y-axis pixels to bottom of cp
    cp_combat = Point(x=545, y=h1)
    cp_inventory = Point(x=646, y=h1)
    cp_equipment = Point(x=678, y=h1)
    cp_prayer = Point(x=713, y=h1)
    cp_spellbook = Point(x=744, y=h1)
    cp_logout = Point(x=646, y=h2)
    cp_settings = Point(x=680, y=h2)

    def __get_inventory_slots() -> list:
        '''
        Returns a 2D list of the inventory slots represented as Points.
        Inventory is 7x4.
        '''
        inv = []
        curr_y = 253
        for _ in range(7):
            curr_x = 583  # reset x
            row = []
            for _ in range(4):
                row.append(Point(curr_x, curr_y))
                curr_x += 42  # x delta
            inv.append(row)
            curr_y += 36  # y delta
        return inv

    inventory_slots = __get_inventory_slots()

    def drop_inventory(self, skip_rows: int = 0) -> None:
        '''
        Drops all items in the inventory.
        Args:
            skip_rows: The number of rows to skip before dropping.
        '''
        self.log_msg("Dropping inventory...")
        pag.keyDown("shift")
        for i, row in enumerate(self.inventory_slots):
            if not self.status_check_passed():
                pag.keyUp("shift")
                return
            if i in range(skip_rows):
                continue
            for slot in row:
                pag.moveTo(slot[0], slot[1])
                time.sleep(0.05)
                pag.click()
        pag.keyUp("shift")

    def friends_nearby(self) -> bool:
        '''
        Checks the minimap for green dots to indicate friends nearby.
        Returns:
            True if friends are nearby, False otherwise.
        '''
        # screenshot minimap
        minimap = bcv.capture_screen(self.rect_minimap)
        # load it as a cv2 image
        minimap = cv2.imread(minimap)
        cv2.imwrite(f"{bcv.TEMP_IMAGES}/minimap.png", minimap)
        # change to hsv
        hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
        cv2.imwrite(f"{bcv.TEMP_IMAGES}/minimap_hsv.png", hsv)
        # Threshold the HSV image to get only friend color
        mask1 = cv2.inRange(hsv, self.TAG_GREEN[0], self.TAG_GREEN[1])
        only_friends = cv2.bitwise_and(minimap, minimap, mask=mask1)
        cv2.imwrite(f"{bcv.TEMP_IMAGES}/minimap_friends.png", only_friends)
        mean = only_friends.mean(axis=(0, 1))
        return str(mean) != "[0. 0. 0.]"

    def get_hp(self) -> int:
        """
        Gets the HP value of the player.
        Returns:
            The HP of the player, or None if not found.
        """
        res = bcv.get_numbers_in_rect(self.rect_hp, True)
        print(res)
        return None if res is None else res[0]

    def get_prayer(self) -> int:
        """
        Gets the prayer value of the player.
        Returns:
            The prayer value of the player, or None if not found.
        """
        res = bcv.get_numbers_in_rect(self.rect_prayer, True)
        print(res)
        return None if res is None else res[0]

    def logout(self):
        '''
        Logs player out.
        '''
        self.log_msg("Logging out...")
        self.mouse.move_to(self.cp_logout)
        pag.click()
        time.sleep(1)
        self.mouse.move_to(Point(645, 451))  # Logout button
        pag.click()
    
    def move_camera_up(self):
        '''
        Moves the camera up.
        '''
        # Position the mouse somewhere on the game view
        self.mouse.move_to(Point(self.rect_game_view.start.x + 20, self.rect_game_view.start.y + 20))
        pag.keyDown('up')
        time.sleep(2)
        pag.keyUp('up')
        time.sleep(0.5)

    def is_in_combat(self) -> bool:
        '''
        Returns whether the player is in combat. This is achieved by checking if text exists in the RuneLite opponent info
        section in the game view, and if that text indicates an NPC is out of HP.
        '''
        result = bcv.get_text_in_rect(self.rect_current_action)
        return result.strip() != ""
    
    def is_player_doing_action(self, action: str):
        '''
        Returns whether the player is doing the given action.
        Args:
            action: The action to check for.
        Returns:
            True if the player is doing the given action, False otherwise.
        Example:
            if self.is_player_doing_action("Woodcutting"):
                print("Player is woodcutting!")
        '''
        return bcv.search_text_in_rect(self.rect_current_action, [action], ["Not"])

    def has_hp_bar(self) -> bool:
        '''
        Returns whether the player has an HP bar above their head.
        This function only works when the game camera is all the way up.
        '''
        # Position of character relative to the screen
        char_pos = Point(self.rect_game_view.end.x / 2 + self.rect_game_view.start.x,
                         self.rect_game_view.end.y / 2 + self.rect_game_view.start.y)
        
        # Make a rectangle around the character
        offset = 30
        char_rect = Rectangle(Point(char_pos.x - offset, char_pos.y - offset*2),
                              Point(char_pos.x + offset, char_pos.y))
        # Take a screenshot of rect
        char_screenshot = bcv.capture_screen(char_rect)
        # Isolate HP bars in that rectangle
        hp_bars = isolate_colors(char_screenshot, [self.TAG_RED, self.TAG_GREEN], "player_hp_bar")
        # If there are any HP bars, return True
        img = cv2.imread(hp_bars)
        return str(img.mean(axis=(0, 1))) != "[0. 0. 0.]"

    def has_hp_bar(self) -> bool:
        '''
        Returns whether the player has an HP bar above their head.
        This function only works when the game camera is all the way up.
        '''
        # Position of character relative to the screen
        char_pos = Point(self.rect_game_view.end.x / 2 + self.rect_game_view.start.x,
                         self.rect_game_view.end.y / 2 + self.rect_game_view.start.y)
        
        # Make a rectangle around the character
        offset = 30
        char_rect = Rectangle(Point(char_pos.x - offset, char_pos.y - offset*2),
                              Point(char_pos.x + offset, char_pos.y))
        # Take a screenshot of rect
        char_screenshot = bcv.capture_screen(char_rect)
        # Isolate HP bars in that rectangle
        hp_bars = isolate_colors(char_screenshot, [self.TAG_RED, self.TAG_GREEN], "player_hp_bar")
        # If there are any HP bars, return True
        img = cv2.imread(hp_bars)
        return str(img.mean(axis=(0, 1))) != "[0. 0. 0.]"

    # --- NPC/Object Detection ---
    def attack_first_tagged(self, game_view: Rectangle) -> bool:
        '''
        Attacks the first-seen tagged NPC that is not already in combat.
        Args:
            game_view: The rectangle to search in.
        Returns:
            True if an NPC attack was attempted, False otherwise.
        '''
        path_game_view = bcv.capture_screen(game_view)
        # Isolate colors in image
        path_npcs = rcv.isolate_colors(path_game_view, [self.TAG_BLUE], "npcs")
        path_hp_bars = rcv.isolate_colors(path_game_view, [self.TAG_GREEN, self.TAG_RED], "hp_bars")
        # Locate potential NPCs in image by determining contours
        contours = rcv.get_contours(path_npcs)
        # Click center pixel of non-combatting NPCs
        img_bgr = cv2.imread(path_hp_bars)
        for cnt in contours:
            try:
                center, top = rcv.get_contour_positions(cnt)
            except Exception:
                print("Cannot find moments of contour. Disregarding...")
                continue
            if not rcv.is_point_obstructed(center, img_bgr):
                self.mouse.move_to(Point(center.x + game_view.start.x, center.y + game_view.start.y), 0.2)
                pag.click()
                return True
        self.log_msg("No tagged NPCs found that aren't in combat.")
        return False

    def get_nearest_tagged_NPC(self, game_view: Rectangle, include_in_combat: bool = False) -> Point:
        '''
        Returns the nearest tagged NPC.
        Args:
            game_view: The rectangle to search in.
        Returns:
            The center point of the nearest tagged NPC, or None if none found.
        '''
        path_game_view = bcv.capture_screen(game_view)
        # Isolate colors in image
        path_npcs = rcv.isolate_colors(path_game_view, [self.TAG_BLUE], "npcs")
        path_hp_bars = rcv.isolate_colors(path_game_view, [self.TAG_GREEN, self.TAG_RED], "hp_bars")
        # Locate potential NPCs in image by determining contours
        contours = rcv.get_contours(path_npcs)
        # Get center pixels of non-combatting NPCs
        centers = []
        img_bgr = cv2.imread(path_hp_bars)
        for cnt in contours:
            try:
                center, top = rcv.get_contour_positions(cnt)
            except Exception:
                print("Cannot find moments of contour. Disregarding...")
                continue
            if not include_in_combat and not rcv.is_point_obstructed(center, img_bgr) or include_in_combat:
                centers.append((center.x, center.y))
        if not centers:
            print("No tagged NPCs found.")
            return None
        dims = img_bgr.shape  # (height, width, channels)
        nearest = self.__get_nearest_point(Point(int(dims[1] / 2), int(dims[0] / 2)), centers)
        return Point(nearest.x + game_view.start.x, nearest.y + game_view.start.y)

    def get_all_tagged_in_rect(self, rect: Rectangle, color: tuple) -> list:
        '''
        Finds all contours on screen of a particular color and returns a list of center Points for each.
        Args:
            rect: The rectangle to search in.
            color: The color to search for. Must be a tuple of (HSV upper, HSV lower) values.
        Returns:
            A list of center Points.
        '''
        path_game_view = bcv.capture_screen(rect)
        path_tagged = rcv.isolate_colors(path_game_view, [color], "get_all_tagged_in_rect")
        contours = rcv.get_contours(path_tagged)
        centers = []
        for cnt in contours:
            try:
                center, _ = rcv.get_contour_positions(cnt)
            except Exception:
                print("Cannot find moments of contour. Disregarding...")
                continue
            centers.append(Point(center.x + rect.start.x, center.y + rect.start.y))
        return centers
    
    def get_nearest_tag(self, color: rcv.Color) -> Point:
        '''
        Finds the nearest contour of a particular color within the game view to the character and returns its center Point.
        Args:
            rect: The rectangle to search in.
            color: The color to search for. Must be a tuple of (HSV upper, HSV lower) values.
        Returns:
            The center Point of the nearest contour, or None if none found.
        '''
        rect = self.rect_game_view
        centers = self.get_all_tagged_in_rect(rect, color)
        return self.__get_nearest_point(Point(int((rect.start.x + rect.end.x) / 2), int((rect.start.y + rect.end.y) / 2)), centers) if centers else None
        

    def __get_nearest_point(self, point: Point, points: list) -> Point:
        '''
        Returns the nearest point in a list of (x, y) coordinates.
        Args:
            point: The point to compare to.
            points: The list of (x, y) coordinates to compare.
        Returns:
            The closest point in the list.
        '''
        point = (point.x, point.y)
        nodes = np.asarray(points)
        dist_2 = np.sum((nodes - point) ** 2, axis=1)
        p = np.argmin(dist_2)
        return Point(points[p][0], points[p][1])

    # --- Client Settings ---
    def __open_display_settings(self) -> bool:
        '''
        Opens the display settings for the game client.
        Returns:
            True if the settings were opened, False if an error occured.
        '''
        cp_settings_selected = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/cp_settings_selected.png",
                                                      self.client_window,
                                                      conf=0.95)
        cp_settings = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/cp_settings.png",
                                             self.client_window,
                                             conf=0.95)
        if cp_settings_selected is None and cp_settings is None:
            self.log_msg("Could not find settings button.")
            return False
        elif cp_settings is not None and cp_settings_selected is None:
            self.mouse.move_to(cp_settings)
            pag.click()
        time.sleep(0.5)
        display_tab = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/cp_settings_display_tab.png", self.client_window)
        if display_tab is None:
            self.log_msg("Could not find the display settings tab.")
            return False
        self.mouse.move_to(display_tab)
        pag.click()
        time.sleep(0.5)
        return True

    def collapse_runelite_settings_panel(self):
        '''
        Identifies the RuneLite settings panel and collapses it.
        '''
        self.log_msg("Closing RuneLite settings panel...")
        settings_icon = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/runelite_settings_collapse.png", self.client_window)
        if settings_icon is not None:
            self.mouse.move_to(settings_icon, 1)
            pag.click()
            time.sleep(1.5)

    def did_set_layout_fixed(self) -> bool:
        '''
        Attempts to set the client's layout to "Fixed - Classic layout".
        Returns:
            True if the layout was set, False if an issue occured.
        '''
        self.log_msg("Setting layout to Fixed - Classic layout.")
        time.sleep(0.3)
        if not self.__open_display_settings():
            return False
        time.sleep(0.3)
        layout_dropdown = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/cp_settings_dropdown.png", self.client_window)
        if layout_dropdown is None:
            self.log_msg("Could not find the layout dropdown.")
            return False
        self.mouse.move_to(layout_dropdown)
        pag.click()
        time.sleep(0.8)
        self.mouse.move_rel(-77, 19, duration=0.2)
        pag.click()
        time.sleep(1.5)
        return True

    def logout_runelite(self):
        '''
        Identifies the RuneLite logout button and clicks it.
        '''
        self.log_msg("Logging out of RuneLite...")
        rl_login_icon = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/runelite_logout.png", self.client_window, conf=0.9)
        if rl_login_icon is not None:
            self.mouse.move_to(rl_login_icon, 0.2)
            pag.click()
            time.sleep(0.2)
            pag.press('enter')
            time.sleep(1)

    def set_camera_zoom(self, percentage: int) -> bool:
        '''
        Sets the camera zoom level.
        Args:
            percentage: The percentage of the camera zoom level to set.
        Returns:
            True if the zoom level was set, False if an issue occured.
        '''
        if percentage < 1:
            percentage = 1
        elif percentage > 100:
            percentage = 100
        self.log_msg(f"Setting camera zoom to {percentage}%...")
        time.sleep(0.3)
        if not self.__open_display_settings():
            return False
        time.sleep(0.3)
        zoom_start = 611
        zoom_end = 708
        x = int((percentage / 100) * (zoom_end - zoom_start) + zoom_start)
        self.mouse.move_to(Point(x, 345), duration=0.2)
        pag.click()
        return True

    # --- Setup Functions ---
    def setup_client(self, window_title: str, set_layout_fixed: bool, logout_runelite: bool, collapse_runelite_settings: bool) -> None:
        # sourcery skip: merge-nested-ifs
        '''
        Configures a RuneLite client window. This function logs messages to the script output log.
        Args:
            window_title: The title of the window to be manipulated. Must match the actual window's title.
            set_layout_fixed: Whether or not to set the layout to "Fixed - Classic layout".
            logout_runelite: Whether to logout of RuneLite during window config.
            collapse_runelite_settings: Whether to close the RuneLite settings panel if it is open.
        '''
        self.log_msg("Configuring client window...")
        time.sleep(1)
        # Get reference to the client window
        try:
            win = pygetwindow.getWindowsWithTitle(window_title)[0]
            win.activate()
        except Exception:
            self.log_msg("Error: Could not find game window.")
            self.set_status(BotStatus.STOPPED)
            return

        # Set window to large initially
        win.moveTo(0, 0)
        self.client_window = Rectangle(Point(0, 0), Point(900, 620))
        win.size = (self.client_window.end.x, self.client_window.end.y)
        time.sleep(1)

        # Set layout to fixed
        if set_layout_fixed:
            if not self.did_set_layout_fixed():  # if layout setup failed
                if pag.confirm("Could not set layout to fixed. Continue anyway?") == "Cancel":
                    self.set_status(BotStatus.STOPPED)
                    return

        # Ensure user is logged out of RuneLite
        if logout_runelite:
            self.logout_runelite()

        # Ensure RuneLite Settings pane is closed
        if collapse_runelite_settings:
            self.collapse_runelite_settings_panel()

        # Move and resize to desired position
        win.moveTo(0, 0)
        self.client_window = Rectangle(Point(0, 0), Point(self.desired_width, self.desired_height))
        win.size = (self.desired_width, self.desired_height)
        time.sleep(1)
        self.log_msg("Client window configured.")
