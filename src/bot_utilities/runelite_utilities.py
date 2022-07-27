'''
runelite_utilities.py is an extension of bot_utilities.py. It contains bot helper functions that are specific to Runelite clients.
'''
from bot_utilities.bot_utilities import Point, Rectangle, TEMP_IMAGES, BOT_IMAGES, capture_screen, search_img_in_rect, search_text_in_rect
import cv2
import numpy as np
import pyautogui as pag
import pygetwindow
import time


# --- Notable Colour Ranges (HSV lower, upper) ---
NPC_BLUE = ((90, 100, 255), (100, 255, 255))
NPC_HP_GREEN = ((40, 100, 255), (70, 255, 255))
NPC_HP_RED = ((0, 255, 255), (20, 255, 255))

# --- Desired client position ---
# Size and position of the smallest possible fixed OSRS client in top left corner of screen.
client_window = Rectangle(start=Point(0, 0), end=Point(809, 534))

# ------- Rects of Interest -------
rect_current_action = Rectangle(Point(10, 52), Point(171, 93))  # combat/skilling plugin text
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


# --- Inventory Slots ---
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
            row.append(Point(x=curr_x, y=curr_y))
            curr_x += 42  # x delta
        inv.append(row)
        curr_y += 36  # y delta
    return inv


inventory_slots = __get_inventory_slots()


def __visit_points():
    '''
    Moves mouse to each defined point of interest.
    TODO: Remove. This is just for testing.
    '''
    pag.moveTo(orb_compass.x, orb_compass.y)
    time.sleep(0.2)
    pag.moveTo(orb_prayer.x, orb_prayer.y)
    time.sleep(0.2)
    pag.moveTo(orb_spec.x, orb_spec.y)
    time.sleep(0.2)
    pag.moveTo(cp_combat.x, cp_combat.y)
    time.sleep(0.2)
    pag.moveTo(cp_inventory.x, cp_inventory.y)
    time.sleep(0.2)
    pag.moveTo(cp_equipment.x, cp_equipment.y)
    time.sleep(0.2)
    pag.moveTo(cp_prayer.x, cp_prayer.y)
    time.sleep(0.2)
    pag.moveTo(cp_spellbook.x, cp_spellbook.y)
    time.sleep(0.2)
    pag.moveTo(cp_logout.x, cp_logout.y)
    time.sleep(0.2)
    pag.moveTo(cp_settings.x, cp_settings.y)
    time.sleep(0.2)
    for row in inventory_slots:
        for slot in row:
            pag.moveTo(slot.x, slot.y)
            time.sleep(0.2)
    pag.moveTo(inventory_slots[2][1].x, inventory_slots[2][1].y)


def toggle_auto_retaliate(toggle_on: bool):
    '''
    Toggles auto retaliate. Assumes client window is configured.
    Args:
        toggle_on: Whether to turn on or off.
    '''
    # click the combat tab
    pag.click(cp_combat.x, cp_combat.y)
    time.sleep(0.5)

    # Search for the auto retaliate button (deselected)
    # If None, then auto retaliate is on.
    auto_retal_btn = search_img_in_rect(f"{BOT_IMAGES}/cp_combat_autoretal.png", rect_inventory, conf=0.9)

    if toggle_on and auto_retal_btn is not None or not toggle_on and auto_retal_btn is None:
        pag.click(644, 402)
    elif toggle_on:
        print("Auto retaliate is already on.")
    else:
        print("Auto retaliate is already off.")


def is_in_combat(expected_enemy_names: list) -> bool:
    '''
    Returns whether the player is in combat.
    TODO: Improve this. Maybe abandon it.
    '''
    # Search for the combat icon
    result = search_text_in_rect(rect_current_action, expected_enemy_names)
    return result is not None


# --- NPC Detection ---
def attack_nearest_tagged() -> bool:
    '''
    Attacks the nearest tagged NPC that is not already in combat.
    Returns:
        True if an NPC attack was attempted, False otherwise.
    '''
    path_game_view = capture_screen(rect_game_view)
    # Isolate colors in image
    path_npcs, path_hp_bars = __isolate_tagged_NPCs_at(path_game_view)
    # Locate potential NPCs in image by determining contours
    contours = __get_contours(path_npcs)
    # Get center pixels of non-combatting NPCs
    centers = []
    img_bgr = cv2.imread(path_hp_bars)
    for cnt in contours:
        try:
            center, top = __get_contour_positions(cnt)
        except Exception:
            print("Cannot find moments of contour. Disregarding...")
            continue
        if not __is_point_obstructed(top, img_bgr):
            centers.append((center.x, center.y))
    if not centers:
        print("No tagged NPCs found.")
        return False
    # Attack nearest NPC
    dims = img_bgr.shape  # (height, width, channels)
    nearest = __get_nearest_point(Point(int(dims[1] / 2), int(dims[0] / 2)), centers)
    pag.click(nearest.x + rect_game_view.start.x, nearest.y + rect_game_view.start.y)
    print("Attacked nearest tagged NPC.")
    return True


def __get_contours(path: str) -> list:
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


def __get_contour_positions(contour) -> tuple:
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


def __get_nearest_point(point: Point, points: list) -> Point:
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


def __is_point_obstructed(point: Point, im) -> bool:
    '''
    This function determines if there are non-black pixels in an image above and below a given point.
    This is useful for determining if an NPC is in combat (E.g., given the top point of an NPC contour
    and a masked image only showing HP bars, determine if the NPC has an HP bar above the contour).
    Args:
        point: The top point of a contour (NPC).
        im: A BGR CV image containing only HP bars.
    Returns:
        True if the point is in combat, False otherwise.
    '''
    # For 10 pixels above/below the point, check if the pixel is not black.
    for i in range(-10, 10):
        try:
            (b, g, r) = im[point.y + i, point.x]
        except Exception:
            continue
        if (b, g, r) != (0, 0, 0):
            print("Detected NPC in combat.")
            return True
    return False


def __isolate_tagged_NPCs_at(path: str) -> str:
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
    mask1 = cv2.inRange(hsv, NPC_BLUE[0], NPC_BLUE[1])
    only_blue = cv2.bitwise_and(img, img, mask=mask1)
    blue_path = f"{TEMP_IMAGES}/only_blue.png"
    cv2.imwrite(blue_path, only_blue)

    # Threshold the original image for green and red
    mask2 = cv2.inRange(hsv, NPC_HP_GREEN[0], NPC_HP_GREEN[1])
    mask3 = cv2.inRange(hsv, NPC_HP_RED[0], NPC_HP_RED[1])
    mask = cv2.bitwise_or(mask2, mask3)
    only_color = cv2.bitwise_and(img, img, mask=mask)
    # Save the image and return path
    color_path = f"{TEMP_IMAGES}/only_green_red.png"
    cv2.imwrite(color_path, only_color)
    return blue_path, color_path


# --- Setup Functions ---
def setup_client(window_title: str, width: int, height: int) -> None:
    '''
    Configures a Runelite client window.
    Args:
        window_title: The title of the window to be manipulated. Must match the actual window's title.
        size: A tuple of the width and height to set the game window to.
    '''
    # Get reference to the client window
    try:
        win = pygetwindow.getWindowsWithTitle(window_title)[0]
        win.activate()
    except Exception:
        print("Error: Could not find Alora window.")
        return

    # Set window to large initially
    temp_win = Rectangle(Point(0, 0), Point(1200, 1000))
    win.moveTo(0, 0)
    win.size = (temp_win.end[0], temp_win.end[1])
    time.sleep(1)

    # Ensure user is logged out of Runelite
    rl_login_icon = search_img_in_rect(f"{BOT_IMAGES}/runelite_logout.png", temp_win, conf=0.9)
    if rl_login_icon is not None:
        pag.click(rl_login_icon.x, rl_login_icon.y)
        time.sleep(0.2)
        pag.press('enter')
        time.sleep(1)

    # Ensure Runelite Settings pane is closed
    settings_icon = search_img_in_rect(f"{BOT_IMAGES}/runelite_settings_selected.png", temp_win)
    if settings_icon is not None:
        pag.click(settings_icon.x, settings_icon.y)
        time.sleep(1)

    # Move and resize to desired position
    win.moveTo(0, 0)
    win.size = (width, height)
    time.sleep(1)
