'''
The RuneliteBot class contains properties and functions that are common across all Runelite-based clients. This class
should be inherited by additional abstract classes representing all bots for a specific game (E.g., Alora, OSRS, etc.).

To determine Thresholds for finding contours: https://pinetools.com/threshold-image
For converting RGB to HSV:
    https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv/48367205#48367205
'''
from abc import ABCMeta
import cv2
from deprecated import deprecated
from model.bot import Bot, BotStatus, Rectangle, Point
import numpy as np
import pyautogui as pag
import pygetwindow
import time


class RuneliteBot(Bot, metaclass=ABCMeta):

    # --- Notable Colour Ranges (HSV lower, HSV upper, threshold) ---
    TAG_BLUE = ((90, 100, 255), (100, 255, 255), 128)       # hex: FF00FFFF
    TAG_PURPLE = ((130, 100, 100), (150, 255, 255), 35)     # hex: FFAA00FF
    TAG_PINK = ((145, 100, 200), (155, 255, 255), 20)       # hex: FFFF00E7
    HP_GREEN = ((40, 100, 255), (70, 255, 255), 128)
    HP_RED = ((0, 255, 255), (20, 255, 255), 128)

    # --- Desired client position ---
    # Size and position of the smallest possible fixed OSRS client in top left corner of screen.
    desired_width, desired_height = (773, 534)
    client_window = None  # client region, determined at setup

    # ------- Main Client Rects -------
    rect_opponent_information = Rectangle(Point(13, 51), Point(140, 87))  # combat/skilling plugin text
    rect_game_view = Rectangle(Point(9, 31), Point(517, 362))  # gameplay area
    rect_hp = Rectangle(Point(528, 81), Point(549, 95))  # hp number on status bar
    rect_prayer = Rectangle(Point(530, 117), Point(550, 130))  # prayer number on status bar
    rect_inventory = Rectangle(Point(554, 230), Point(737, 491))  # inventory area
    rect_minimap = Rectangle(Point(523, 29), Point(753, 188))  # minimap area

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

    def get_hp(self) -> int:
        """
        Gets the HP value of the player.
        Returns:
            The HP of the player, or None if not found.
        """
        res = self.get_numbers_in_rect(self.rect_hp, True)
        print(res)
        return None if res is None else res[0]

    def get_prayer(self) -> int:
        """
        Gets the prayer value of the player.
        Returns:
            The prayer value of the player, or None if not found.
        """
        res = self.get_numbers_in_rect(self.rect_prayer, True)
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

    def is_in_combat(self) -> bool:
        '''
        Returns whether the player is in combat. This is achieved by checking if text exists in the Runelite opponent info
        section in the game view, and if that text indicates an NPC is out of HP.
        '''
        result = self.get_text_in_rect(self.rect_opponent_information)
        return result.strip() != ""
    
    # --- NPC Detection ---
    def attack_first_tagged(self, game_view: Rectangle) -> bool:
        '''
        Attacks the first-seen tagged NPC that is not already in combat.
        Args:
            game_view: The rectangle to search in.
        Returns:
            True if an NPC attack was attempted, False otherwise.
        '''
        path_game_view = self.capture_screen(game_view)
        # Isolate colors in image
        path_npcs, path_hp_bars = self.__isolate_tags_at(path_game_view)
        # Locate potential NPCs in image by determining contours
        contours = self.__get_contours(path_npcs)
        # Click center pixel of non-combatting NPCs
        img_bgr = cv2.imread(path_hp_bars)
        for cnt in contours:
            try:
                center, top = self.__get_contour_positions(cnt)
            except Exception:
                print("Cannot find moments of contour. Disregarding...")
                continue
            if not self.__is_point_obstructed(center, img_bgr):
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
        path_game_view = self.capture_screen(game_view)
        # Isolate colors in image
        path_npcs, path_hp_bars = self.__isolate_tags_at(path_game_view)
        # Locate potential NPCs in image by determining contours
        contours = self.__get_contours(path_npcs, self.TAG_BLUE[2])
        # Get center pixels of non-combatting NPCs
        centers = []
        img_bgr = cv2.imread(path_hp_bars)
        for cnt in contours:
            try:
                center, top = self.__get_contour_positions(cnt)
            except Exception:
                print("Cannot find moments of contour. Disregarding...")
                continue
            if not include_in_combat and not self.__is_point_obstructed(center, img_bgr) or include_in_combat:
                centers.append((center.x, center.y))
        if not centers:
            print("No tagged NPCs found.")
            return None
        dims = img_bgr.shape  # (height, width, channels)
        nearest = self.get_nearest_point(Point(int(dims[1] / 2), int(dims[0] / 2)), centers)
        return Point(nearest.x + game_view.start.x, nearest.y + game_view.start.y)

    def get_all_tagged_in_rect(self, rect: Rectangle, color: tuple) -> list:
        '''
        Finds all contours on screen of a particular color and returns a list of center Points for each.
        Args:
            rect: The rectangle to search in.
            color: The color to search for. Must be a tuple of (HSV upper, HSV lower, threshold) values.
        Returns:
            A list of center Points.
        '''
        path_game_view = self.capture_screen(rect)
        path_tagged = self.__isolate_color(path=path_game_view, color=color, filename="get_all_tagged_in_rect")
        contours = self.__get_contours(path_tagged, color[2])
        centers = []
        for cnt in contours:
            try:
                center, _ = self.__get_contour_positions(cnt)
            except Exception:
                print("Cannot find moments of contour. Disregarding...")
                continue
            centers.append(Point(center.x + rect.start.x, center.y + rect.start.y))
        return centers

    def __get_contours(self, path: str, thresh: int) -> list:
        '''
        Gets the contours of an image.
        Args:
            path: The path to the image.
            thresh: The threshold to use for the image.
        Returns:
            A list of contours.
        '''
        img = cv2.imread(path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(img_gray, thresh, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def __get_contour_positions(self, contour) -> tuple:
        '''
        Gets the center and top pixel positions of a contour.
        Args:
            contour: The contour to get the positions of.
        Returns:
            A center and top pixel positions as Points.
        '''
        moments = cv2.moments(contour)
        center_x = int(moments["m10"] / moments["m00"])
        center_y = int(moments["m01"] / moments["m00"])
        top_x, top_y = contour[contour[..., 1].argmin()][0]
        return Point(center_x, center_y), Point(top_x, top_y)

    def get_nearest_point(self, point: Point, points: list) -> Point:
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

    def __is_point_obstructed(self, point: Point, im, span: int = 20) -> bool:
        '''
        This function determines if there are non-black pixels in an image around a given point.
        This is useful for determining if an NPC is in combat (E.g., given the top point of an NPC contour
        and a masked image only showing HP bars, determine if the NPC has an HP bar around the contour).
        Args:
            point: The top point of a contour (NPC).
            im: A BGR CV image containing only HP bars.
            span: The number of pixels to search around the given point.
        Returns:
            True if the point is obstructed, False otherwise.
        '''
        try:
            crop = im[point.y-span:point.y+span, point.x-span:point.x+span]
            mean = crop.mean(axis=(0, 1))
            return str(mean) != "[0. 0. 0.]"
        except Exception:
            print("Cannot crop image. Disregarding...")
            return True

    @deprecated(reason="Use __isolate_color() instead.")
    def __isolate_tags_at(self, path: str) -> str:
        '''
        Isolates Runelite tags and saves them as images. Useful for identifying tagged NPCs, and health bars.
        Args:
            path: The path to the image to isolate colors.
        Returns:
            The paths to an image with only blue tagged contours, and an image with only green/red.
        '''
        img = cv2.imread(path)
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only blue color
        mask1 = cv2.inRange(hsv, self.TAG_BLUE[0], self.TAG_BLUE[1])
        only_blue = cv2.bitwise_and(img, img, mask=mask1)
        blue_path = f"{self.TEMP_IMAGES}/only_blue.png"
        cv2.imwrite(blue_path, only_blue)

        # Threshold the original image for green and red
        mask2 = cv2.inRange(hsv, self.HP_GREEN[0], self.HP_GREEN[1])
        mask3 = cv2.inRange(hsv, self.HP_RED[0], self.HP_RED[1])
        mask = cv2.bitwise_or(mask2, mask3)
        only_color = cv2.bitwise_and(img, img, mask=mask)
        # Save the image and return path
        color_path = f"{self.TEMP_IMAGES}/only_green_red.png"
        cv2.imwrite(color_path, only_color)
        return blue_path, color_path

    def __isolate_color(self, path: str, color: tuple, filename: str) -> str:
        '''
        Isolates contours of a particular color and saves them as images.
        Args:
            path: The path to the image to isolate colors.
            color: A two-part tuple containing the lower and upper bounds of the HSV color being isolated.
            save_as: The name of the file to be saved in the temp images folder.
        Returns:
            The path to an image with only the desired color.
        '''
        img = cv2.imread(path)
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only blue color
        mask = cv2.inRange(hsv, color[0], color[1])
        only_color = cv2.bitwise_and(img, img, mask=mask)
        # Save the image and return path
        color_path = f"{self.TEMP_IMAGES}/{filename}.png"
        cv2.imwrite(color_path, only_color)
        return color_path

    def __open_display_settings(self) -> bool:
        '''
        Opens the display settings for the game client.
        Returns:
            True if the settings were opened, False if an error occured.
        '''
        cp_settings_selected = self.search_img_in_rect(f"{self.BOT_IMAGES}/cp_settings_selected.png",
                                                       self.client_window,
                                                       conf=0.95)
        cp_settings = self.search_img_in_rect(f"{self.BOT_IMAGES}/cp_settings.png",
                                              self.client_window,
                                              conf=0.95)
        if cp_settings_selected is None and cp_settings is None:
            self.log_msg("Could not find settings button.")
            return False
        elif cp_settings is not None and cp_settings_selected is None:
            self.mouse.move_to(cp_settings)
            pag.click()
        time.sleep(0.5)
        display_tab = self.search_img_in_rect(f"{self.BOT_IMAGES}/cp_settings_display_tab.png", self.client_window)
        if display_tab is None:
            self.log_msg("Could not find the display settings tab.")
            return False
        self.mouse.move_to(display_tab)
        pag.click()
        time.sleep(0.5)
        return True

    # --- Client Settings ---
    def collapse_runelite_settings_panel(self):
        '''
        Identifies the Runelite settings panel and collapses it.
        '''
        self.log_msg("Closing Runelite settings panel...")
        settings_icon = self.search_img_in_rect(f"{self.BOT_IMAGES}/runelite_settings_collapse.png", self.client_window)
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
        layout_dropdown = self.search_img_in_rect(f"{self.BOT_IMAGES}/cp_settings_dropdown.png", self.client_window)
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
        Identifies the Runelite logout button and clicks it.
        '''
        self.log_msg("Logging out of Runelite...")
        rl_login_icon = self.search_img_in_rect(f"{self.BOT_IMAGES}/runelite_logout.png", self.client_window, conf=0.9)
        if rl_login_icon is not None:
            self.mouse.move_to(rl_login_icon, duration=1)
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
        Configures a Runelite client window. This function logs messages to the script output log.
        Args:
            window_title: The title of the window to be manipulated. Must match the actual window's title.
            set_layout_fixed: Whether or not to set the layout to "Fixed - Classic layout".
            logout_runelite: Whether to logout of Runelite during window config.
            collapse_runelite_settings: Whether to close the Runelite settings panel if it is open.
        '''
        self.log_msg("Configuring client window...")
        time.sleep(1)
        # Get reference to the client window
        try:
            win = pygetwindow.getWindowsWithTitle(window_title)[0]
            win.activate()
        except Exception:
            self.log_msg("Error: Could not find game window.")
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

        # Ensure user is logged out of Runelite
        if logout_runelite:
            self.logout_runelite()

        # Ensure Runelite Settings pane is closed
        if collapse_runelite_settings:
            self.collapse_runelite_settings_panel()

        # Move and resize to desired position
        win.moveTo(0, 0)
        self.client_window = Rectangle(Point(0, 0), Point(self.desired_width, self.desired_height))
        win.size = (self.desired_width, self.desired_height)
        time.sleep(1)
        self.log_msg("Client window configured.")
