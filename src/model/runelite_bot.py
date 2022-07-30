'''
The RuneliteBot class contains properties and functions that are common across all Runelite-based clients. This class
should be inherited by additional abstract classes representing all bots for a specific game (E.g., Alora, OSRS, etc.).
'''
from abc import ABCMeta
import cv2
from model.bot import Bot, Rectangle, Point
import numpy as np
import pyautogui as pag
import pygetwindow
import time


class RuneliteBot(Bot, metaclass=ABCMeta):

    # --- Notable Colour Ranges (HSV lower, upper) ---
    NPC_BLUE = ((90, 100, 255), (100, 255, 255))
    NPC_HP_GREEN = ((40, 100, 255), (70, 255, 255))
    NPC_HP_RED = ((0, 255, 255), (20, 255, 255))

    # --- Desired client position ---
    # Size and position of the smallest possible fixed OSRS client in top left corner of screen.
    client_window = Rectangle(start=Point(0, 0), end=Point(809, 534))

    # ------- Rects of Interest -------
    rect_opponent_information = Rectangle(Point(13, 51), Point(140, 87))  # combat/skilling plugin text
    rect_game_view = Rectangle(Point(9, 31), Point(517, 362))  # gameplay area
    rect_hp = Rectangle(Point(526, 80), Point(552, 100))  # contains HP text value
    rect_inventory = Rectangle(Point(554, 230), Point(737, 491))  # inventory area
    # TODO: Add more rectangles of interest (prayer, spec, etc.)

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
                row.append((curr_x, curr_y))
                curr_x += 42  # x delta
            inv.append(row)
            curr_y += 36  # y delta
        return inv

    inventory_slots = __get_inventory_slots()

    def drop_inventory(self):
        '''
        Drops all items in the inventory.
        '''
        self.log_msg("Dropping inventory...")
        pag.keyDown("shift")
        for row in self.inventory_slots:
            if self.status_check_passed():
                return
            for slot in row:
                pag.moveTo(slot[0], slot[1])
                time.sleep(0.05)
                pag.click()
        pag.keyUp("shift")

    def is_in_combat(self) -> bool:
        '''
        Returns whether the player is in combat. This is achieved by checking if text exists in the Runelite opponent info
        section in the game view, and if that text indicates an NPC is out of HP.
        '''
        result = self.get_text_in_rect(self.rect_opponent_information)
        return "0/" in result or result.strip() != ""

    # --- NPC Detection ---
    def attack_nearest_tagged(self, game_view: Rectangle) -> bool:
        '''
        Attacks the nearest tagged NPC that is not already in combat.
        Args:
            game_view: The rectangle to search in.
        Returns:
            True if an NPC attack was attempted, False otherwise.
        '''
        path_game_view = self.capture_screen(game_view)
        # Isolate colors in image
        path_npcs, path_hp_bars = self.__isolate_tagged_NPCs_at(path_game_view)
        # Locate potential NPCs in image by determining contours
        contours = self.__get_contours(path_npcs)
        # Get center pixels of non-combatting NPCs
        centers = []
        img_bgr = cv2.imread(path_hp_bars)
        for cnt in contours:
            try:
                center, top = self.__get_contour_positions(cnt)
            except Exception:
                print("Cannot find moments of contour. Disregarding...")
                continue
            if not self.__is_point_obstructed(top, img_bgr):
                centers.append((center.x, center.y))
        if not centers:
            print("No tagged NPCs found.")
            return False
        # Attack nearest NPC
        dims = img_bgr.shape  # (height, width, channels)
        nearest = self.__get_nearest_point(Point(int(dims[1] / 2), int(dims[0] / 2)), centers)
        self.mouse.move_to((nearest.x + game_view.start.x, nearest.y + game_view.start.y), 0.2)
        pag.click()
        print("Attacked nearest tagged NPC.")
        return True

    def __get_contours(self, path: str) -> list:
        '''
        Gets the contours of an image.
        Args:
            path: The path to the image.
        Returns:
            A list of contours.
        '''
        img = cv2.imread(path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY)
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

    def __is_point_obstructed(self, point: Point, im, kernel: int = 10) -> bool:
        '''
        This function determines if there are non-black pixels in an image around a given point.
        This is useful for determining if an NPC is in combat (E.g., given the top point of an NPC contour
        and a masked image only showing HP bars, determine if the NPC has an HP bar around the contour).
        Args:
            point: The top point of a contour (NPC).
            im: A BGR CV image containing only HP bars.
        Returns:
            True if the point is obstructed, False otherwise.
        '''
        try:
            crop = im[point.y-kernel:point.y+kernel, point.x-kernel:point.x+kernel]
        except Exception:
            print("Cannot crop image. Disregarding...")
            return True
        mean = crop.mean(axis=(0, 1))
        if str(mean) != "[0. 0. 0.]":
            return True
        return False

    def __isolate_tagged_NPCs_at(self, path: str) -> str:
        '''
        Isolates tagged NPCs, HP bars and hitsplats in an image.
        Args:
            path: The path to the image to isolate colors.
        Returns:
            The paths to an image with only tagged NPCs, and an image with only HP bars.
        '''
        img = cv2.imread(path)
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only blue color
        mask1 = cv2.inRange(hsv, self.NPC_BLUE[0], self.NPC_BLUE[1])
        only_blue = cv2.bitwise_and(img, img, mask=mask1)
        blue_path = f"{self.TEMP_IMAGES}/only_blue.png"
        cv2.imwrite(blue_path, only_blue)

        # Threshold the original image for green and red
        mask2 = cv2.inRange(hsv, self.NPC_HP_GREEN[0], self.NPC_HP_GREEN[1])
        mask3 = cv2.inRange(hsv, self.NPC_HP_RED[0], self.NPC_HP_RED[1])
        mask = cv2.bitwise_or(mask2, mask3)
        only_color = cv2.bitwise_and(img, img, mask=mask)
        # Save the image and return path
        color_path = f"{self.TEMP_IMAGES}/only_green_red.png"
        cv2.imwrite(color_path, only_color)
        return blue_path, color_path

    # --- Setup Functions ---
    def setup_client(self, window_title: str, logout_runelite: bool, close_runelite_settings: bool) -> None:
        '''
        Configures a Runelite client window. This function logs messages to the script output log.
        Args:
            window_title: The title of the window to be manipulated. Must match the actual window's title.
            logout_runelite: Whether to logout of Runelite during window config.
            close_runelite_settings: Whether to close the Runelite settings panel if it is open.
        '''
        self.log_msg("Configuring client window...")
        # Get reference to the client window
        try:
            win = pygetwindow.getWindowsWithTitle(window_title)[0]
            win.activate()
        except Exception:
            self.log_msg("Error: Could not find game window.")
            return

        # Set window to large initially
        temp_win = Rectangle(Point(0, 0), Point(1200, 1000))
        win.moveTo(0, 0)
        win.size = (temp_win.end[0], temp_win.end[1])
        time.sleep(1)

        # Ensure user is logged out of Runelite
        if logout_runelite:
            self.log_msg("Logging out of Runelite...")
            rl_login_icon = self.search_img_in_rect(f"{self.BOT_IMAGES}/runelite_logout.png", temp_win, conf=0.9)
            if rl_login_icon is not None:
                self.mouse.move_to(rl_login_icon, duration=1)
                pag.click()
                time.sleep(0.2)
                pag.press('enter')
                time.sleep(1)

        # Ensure Runelite Settings pane is closed
        if close_runelite_settings:
            self.log_msg("Closing Runelite settings panel...")
            settings_icon = self.search_img_in_rect(f"{self.BOT_IMAGES}/runelite_settings_selected.png", temp_win)
            if settings_icon is not None:
                self.mouse.move_to(settings_icon, 1)
                pag.click()
                time.sleep(1)

        # Move and resize to desired position
        win.moveTo(0, 0)
        win.size = (self.client_window.end.x, self.client_window.end.y)
        time.sleep(1)
        self.log_msg("Client window configured.")