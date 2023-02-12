import json
import os
import shutil
import time
from pathlib import Path
from typing import List, NamedTuple

import pyautogui
import win32clipboard

import utilities.api.item_ids as item_ids
import utilities.color as clr
import utilities.debug as debug
import utilities.game_launcher as launcher
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Rectangle, RuneLiteObject
from utilities.random_util import truncated_normal_sample

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# TODO movement refactor. Integrate it in the Bot class? It needs API and mouse access
# TODO mouse.move_to on right click menu rarely can un-show the right click menu, if it picks a bad curve


GroundMarker = NamedTuple("GroundMarker", regionId=int, regionX=int, regionY=int, z=int, color=str, label=str)


class DelayTicks(NamedTuple):
    ZERO = truncated_normal_sample(0.08, 0.16, 0.11)
    ONE = truncated_normal_sample(0.4, 0.7, 0.55)
    TWO = truncated_normal_sample(0.9, 1.3, 1.18)
    THREE = truncated_normal_sample(1.6, 2.1, 1.81)
    FOUR = truncated_normal_sample(2.18, 2.69, 2.43)


class OSRSCooksAssistant(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Cooks Assistant"
        description = "Does the Cook's Assistant quest in 10 minutes or less, or your money back!"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 10
        self.api_morg = MorgHTTPSocket()
        self.api_status = StatusSocket()

    def create_options(self):
        pass

    def save_options(self, options: dict):
        self.log_msg("Using preconfigured options")
        self.options_set = True

    def launch_game(self):
        if launcher.is_program_running("RuneLite"):
            self.log_msg("RuneLite is already running. Please close it and try again.")
            return
        # Make a copy of the default settings and save locally
        src = launcher.runelite_settings_folder.joinpath("osrs_settings.properties")
        dst = Path(__file__).parent.joinpath("custom_settings.properties")
        shutil.copy(str(src), str(dst))
        # Modify the highlight list
        with dst.open() as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("npcindicators.npcToHighlight="):
                lines[i] = "npcindicators.npcToHighlight=shop keeper, cook\n"
            elif line.startswith("groundMarker.borderWidth="):
                lines[i] = "groundMarker.borderWidth=0.0\n"
            elif line.startswith("objectindicators.borderWidth="):
                lines[i] = "objectindicators.borderWidth=5.0\n"
            elif line.startswith("objectindicators.rememberObjectColors="):
                lines[i] = "objectindicators.rememberObjectColors=true\n"
            elif line.startswith("grounditems.highlightedItems="):
                lines[i] = "grounditems.highlightedItems=Egg\n"
        lines.extend(
            [
                (
                    'objectindicators.region_12595=[{"id"\:1521,"name"\:"Large'
                    ' door","regionId"\:12595,"regionX"\:30,"regionY"\:38,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:1522,"name"\:"Large'
                    ' door","regionId"\:12595,"regionX"\:30,"regionY"\:39,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:12988,"name"\:"Gate","regionId"\:12595,"regionX"\:52,"regionY"\:16,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:12966,"name"\:"Ladder","regionId"\:12595,"regionX"\:28,"regionY"\:43,"z"\:2,"color"\:"\#FFFAFF00"},{"id"\:1559,"name"\:"Gate","regionId"\:12595,"regionX"\:27,"regionY"\:25,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:1558,"name"\:"Gate","regionId"\:12595,"regionX"\:27,"regionY"\:26,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:15506,"name"\:"Wheat","regionId"\:12595,"regionX"\:26,"regionY"\:30,"z"\:0,"color"\:"\#FFFF0A00"},{"id"\:883,"name"\:"Gate","regionId"\:12595,"regionX"\:40,"regionY"\:51,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:12965,"name"\:"Ladder","regionId"\:12595,"regionX"\:28,"regionY"\:43,"z"\:1,"color"\:"\#FFFAFF00"},{"id"\:15507,"name"\:"Wheat","regionId"\:12595,"regionX"\:25,"regionY"\:28,"z"\:0,"color"\:"\#FFFF0A00"},{"id"\:12964,"name"\:"Ladder","regionId"\:12595,"regionX"\:28,"regionY"\:43,"z"\:0,"color"\:"\#FFFAFF00"},{"id"\:24961,"name"\:"Hopper","regionId"\:12595,"regionX"\:31,"regionY"\:43,"z"\:2,"color"\:"\#FFFF9A00"},{"id"\:24964,"name"\:"Hopper'
                    ' controls","regionId"\:12595,"regionX"\:30,"regionY"\:41,"z"\:2,"color"\:"\#FFFF4D00"},{"id"\:1781,"name"\:"Flour'
                    ' bin","regionId"\:12595,"regionX"\:31,"regionY"\:43,"z"\:0,"color"\:"\#FFFF0043"},{"id"\:23918,"name"\:"Gate","regionId"\:12595,"regionX"\:40,"regionY"\:52,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:12986,"name"\:"Gate","regionId"\:12595,"regionX"\:52,"regionY"\:15,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:8689,"name"\:"Dairy'
                    ' cow","regionId"\:12595,"regionX"\:36,"regionY"\:54,"z"\:0,"color"\:"\#FFFF4D00"},{"id"\:15506,"name"\:"Wheat","regionId"\:12595,"regionX"\:24,"regionY"\:30,"z"\:0,"color"\:"\#FFFF0A00"}]\n'
                ),
                'objectindicators.region_12850=[{"id"\:1541,"name"\:"Door","regionId"\:12850,"regionX"\:14,"regionY"\:45,"z"\:0,"color"\:"\#FFFF00E7"},{"id"\:1540,"name"\:"Door","regionId"\:12850,"regionX"\:15,"regionY"\:45,"z"\:0,"color"\:"\#FFFF00E7"}]\n',
            ]
        )
        with dst.open("w") as f:
            f.writelines(lines)
        # Launch the game
        launcher.launch_runelite_with_settings(self, dst)

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to set the status to STOPPED.

        Additional notes:
        Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
        Visit the Wiki for more.
        """
        # Setup APIs

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        while not self.api_morg.test_endpoints():
            time.sleep(0.3)
        self.log_msg("Morg API is ready")

        while time.time() - start_time < end_time:
            # TODO Enforce north facing camera, and a mostly top-down view

            self.navigate_path("lumby_to_general_store")
            self.maybe_open_nearest_door()

            self.interact_highlighted_npc(["Trade"])
            self.buy_item_from_shop("Pot.png")
            self.buy_item_from_shop("Bucket.png")
            self.press_keyboard_key("esc")

            self.load_ground_markers("general_store_to_fred")
            self.maybe_open_nearest_door()
            self.navigate_path("general_store_to_fred", import_markers=False)
            self.maybe_open_nearest_door()

            # TODO Maybe use northern chicken pen
            self.loot_egg()

            self.load_ground_markers("fred_to_wheat_field")
            self.maybe_open_nearest_door()
            self.navigate_path("fred_to_wheat_field", import_markers=False)
            self.maybe_open_nearest_door()

            self.scavenge_wheat()

            self.load_ground_markers("wheat_field_to_windmill")
            self.maybe_open_nearest_door()
            self.navigate_path("wheat_field_to_windmill", import_markers=False)
            self.maybe_open_nearest_door()

            self.climb_nearest_ladder(direction="up")
            self.climb_nearest_ladder(direction="up")
            self.operate_hopper()
            self.climb_nearest_ladder(direction="down")
            self.climb_nearest_ladder(direction="down")
            self.empty_flour_bin()

            # Import markers ahead of time to rapidly leave building
            self.load_ground_markers("windmill_to_cowpen")
            self.maybe_open_nearest_door()
            self.navigate_path("windmill_to_cowpen", import_markers=False)
            self.maybe_open_nearest_door()

            self.milk_cow()

            # Import markers ahead of time to rapidly leave building
            self.load_ground_markers("cowpen_to_lumby_kitchen")
            self.maybe_open_nearest_door()
            self.navigate_path("cowpen_to_lumby_kitchen", import_markers=False)

            self.appease_cook()

            break

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def press_keyboard_key(self, key: str):
        # TODO Keyboard class
        pyautogui.keyDown(key)
        LOWER_BOUND_CLICK = 0.03  # Milliseconds
        UPPER_BOUND_CLICK = 0.2  # Milliseconds
        AVERAGE_CLICK = 0.06  # Milliseconds
        time.sleep(truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pyautogui.keyUp(key)
        time.sleep(truncated_normal_sample(0.1, 0.4, 0.3))

    def tile_label_generator(self, start, stop, is_initializing=False):
        # TODO Refactor to movement module
        if not is_initializing:
            # This assert is just to avoid finding duplicate tiles,
            # since there are only 234 unique labels
            # There really shouldn't be this many tagged tiles in the game view...
            assert stop - start < 234, "Attempting to travel too many tiles"

        while start < stop:
            alpha = chr(ord("A") + (start % 26))
            digit = ((start % 234) // 26) + 1  # 1-9 only
            yield start, f"{alpha}{digit}"
            start += 1

    def load_ground_markers(self, name: str, generate_labels=True, import_markers=True) -> list[GroundMarker]:
        # TODO Refactor to movement module
        f = open(os.path.join(__location__, f"objective_paths/{name}.json"))
        tile_path = json.load(f)
        f.close()

        if not import_markers:
            return tile_path

        if generate_labels:
            for index, label in self.tile_label_generator(0, len(tile_path), is_initializing=True):
                tile_path[index]["label"] = label

        # TODO Inject directly into temp.properties?
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(json.dumps(tile_path))
        win32clipboard.CloseClipboard()

        self.interact_ground_markers(action="import")
        return tile_path

    def clear_ground_markers(self):
        self.interact_ground_markers(action="clear")

    def interact_ground_markers(self, action="import"):
        self.mouse.move_to(self.win.world_map_orb.random_point())
        self.mouse.right_click()
        # TODO Right click menu OCR
        ground_marker_options = ocr.find_text("Ground Markers", self.win.game_view, ocr.BOLD_12, clr.ORANGE)
        if len(ground_marker_options) != 2:
            self.log_msg("Only expected 2 ground marker options due to right-click menu OCR bug")
            self.stop()
        ground_marker_options = sorted(ground_marker_options, key=lambda r: Rectangle.distance_from(r, self.win.world_map_orb.get_center()))

        action_rect = 0 if action == "import" else 1
        self.mouse.move_to(ground_marker_options[action_rect].random_point())
        self.mouse.click()
        time.sleep(truncated_normal_sample(0.1, 0.4, 0.25))
        self.press_keyboard_key("num1")

    def navigate_path(
        self,
        path_file: str,
        import_markers=True,
        clear_markers=True,
    ):
        # TODO Refactor to movement module
        path = self.load_ground_markers(path_file, import_markers=import_markers)

        furthest_tile_found = 0
        while True:
            # If we are moving
            if not self.api_morg.get_is_player_idle():
                # Wait until idle 15% of the time
                if rd.random_chance(0.15):
                    self.wait_until_idle()
                # Otherwise attempt to navigate again in a few ticks
                else:
                    time.sleep(truncated_normal_sample(1.21, 4.86, 2.38))

            _candidate_furthest_tile = furthest_tile_found
            _candidate_furthest_rectangle: Rectangle = None

            # Find the furthest tile we can navigate to
            # Start scanning a few tiles back in case pathing shifts some tiles out of view

            tile_scan_range = max(furthest_tile_found - 5, 0), furthest_tile_found + 50

            start = time.time_ns() // 1_000_000

            next_tiles_in_path = [label for _, label in self.tile_label_generator(tile_scan_range[0], tile_scan_range[1])]
            self.log_msg(f"Scanning for tiles from {next_tiles_in_path[0]} to {next_tiles_in_path[-1]}")
            next_found_tiles = ocr.find_text(next_tiles_in_path, self.win.game_view, ocr.PLAIN_11, clr.GREEN, return_dict=True)

            for index, label in self.tile_label_generator(tile_scan_range[0], tile_scan_range[1]):
                rects_for_tile = next_found_tiles.get(label, [])
                # print(f'Checking tiling: {index} {label}. Tiles found: {len(rects_for_tile)}')
                if len(rects_for_tile) == 1:
                    _candidate_furthest_rectangle = rects_for_tile[0]
                    _candidate_furthest_tile = label
                    furthest_tile_found = index
                else:
                    continue

            end = time.time_ns() // 1_000_000
            # This takes ~ 500ms, not great for moving while walking
            print(f"OCR tile parse took {round(end - start, 2)} ms.")

            if _candidate_furthest_rectangle is None:
                self.log_msg("Found no tiles!")
                self.stop()
                break

            self.log_msg(f"Navigating to: {furthest_tile_found} - {_candidate_furthest_tile} - {_candidate_furthest_rectangle}")
            self.mouse.move_to(_candidate_furthest_rectangle.random_point())
            self.walk_here()

            if furthest_tile_found == len(path) - 1:
                self.log_msg("Navigated to end of path")
                self.wait_until_idle()
                break

        if clear_markers:
            self.clear_ground_markers()

    def maybe_open_nearest_door(self):
        """
        Open the nearest door if it is closed
        """
        # TODO Refactor to movement module
        doors = self.get_all_tagged_in_rect(self.win.game_view, ObjectColors.DOOR)
        doors = sorted(doors, key=RuneLiteObject.distance_from_rect_center)

        if not len(doors):
            self.log_msg("Couldnt find any doors")
            self.stop()

        self.mouse.move_to(doors[0].random_point())
        self.mouse.right_click()
        close_option = ocr.find_text("Close", self.win.game_view, ocr.BOLD_12, clr.WHITE)
        cancel_option = ocr.find_text("Cancel", self.win.game_view, ocr.BOLD_12, clr.WHITE)
        # TODO Right menu OCR to explicitly check "Open"
        if not close_option:
            self.mouse.move_to(cancel_option[0].random_point())
            self.mouse.click()
            self.mouse.move_to(doors[0].random_point())
            self.mouse.click()
        else:
            self.mouse.move_to(cancel_option[0].random_point())
            self.mouse.click()

        self.wait_until_idle(delay=DelayTicks.ZERO)

    def climb_nearest_ladder(self, direction="up"):
        """
        Climb the nearest ladder in the specified direction
        """
        # TODO Refactor to movement module
        ladders = self.get_all_tagged_in_rect(self.win.game_view, ObjectColors.LADDER)
        ladders = sorted(ladders, key=RuneLiteObject.distance_from_rect_center)

        if not len(ladders):
            self.log_msg("Couldnt find any ladders")
            self.stop()

        # TODO Handle dead clicks inside hull
        self.mouse.move_to(ladders[0].random_point())
        self.mouse.right_click()
        cancel_option = ocr.find_text("Cancel", self.win.game_view, ocr.BOLD_12, clr.WHITE)

        # TODO Right click menu OCR to explicitly check "Climb-up", "Climb-down"
        if climb_options := ocr.find_text(
            "Climb",
            self.win.game_view,
            ocr.BOLD_12,
            clr.WHITE,
        ):
            climb_options = sorted(climb_options, key=lambda rect: Rectangle.distance_from(rect, point=cancel_option[0].get_center()))
            if len(climb_options) == 1:
                self.mouse.move_to(climb_options[0].random_point())
            elif direction == "up":
                self.mouse.move_to(climb_options[1].random_point())
            elif direction == "down":
                self.mouse.move_to(climb_options[0].random_point())
            self.mouse.click()

        self.wait_until_idle(delay=DelayTicks.TWO)  # Maybe screen is loading? Not sure if idle API captures this

    def buy_item_from_shop(self, img_file: str, quantity=1):
        shop_item = imsearch.search_img_in_rect(
            imsearch.BOT_IMAGES.joinpath("items", img_file),
            self.win.game_view,  # TODO Only in shop rectangle, get shop PNG skeleton
            confidence=0.1,  # 0.15 grabs random items in general store scenery when searching Pot
        )
        self.log_msg(f"Looked for pot: {shop_item}")
        if shop_item:
            pot_point = shop_item.random_point()
            self.mouse.move_to(pot_point)
            self.mouse.right_click()
            # TODO Right click menu OCR
            self.mouse.move_to((pot_point.x - 15, pot_point.y + 40), mouseSpeed="medium")  # TODO Randomize
            self.mouse.click()

        self.log_msg(f"Bought {quantity} {img_file} from shop")
        time.sleep(truncated_normal_sample(0.3, 0.7, 0.57))

    def interact_highlighted_npc(self, click_pattern: List[str]):
        """
        Assumes all highlighted npcs are the same

        `click_pattern` is a union type of mouse clicks and standard OSRS actions
        E.g.
        - ['left'] for normal left click
        - ['Trade'] will only left click if the 'Trade' option is in mouseover
        - ['right', 'Pickpocket'] to pickpocket without menu entry swapper
        """
        # TODO Rewrite this def
        current_step = 0

        while current_step < len(click_pattern):
            highlighted_npcs = self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN)
            if not len(highlighted_npcs):
                self.log_msg("Couldnt find any highlighted npcs")
                self.stop()
            self.mouse.move_to(highlighted_npcs[0].random_point())
            current_action = click_pattern[current_step]
            if not self.mouseover_text(contains=current_action, color=clr.OFF_WHITE):
                # The NPC may be moving, try again in some time
                time.sleep(truncated_normal_sample(0.3, 0.5, 0.43))
                continue
            self.mouse.click()
            self.wait_until_idle()
            current_step += 1

    def loot_egg(self):
        start_time = time.time()
        end_time = self.running_time * 60

        while not self.api_morg.get_if_item_in_inv(item_ids.EGG) and time.time() - start_time < end_time:
            self.log_msg("Trying to loot the egg...")
            self.pick_up_loot("Egg")
            self.wait_until_idle()
        self.log_msg("Got the egg!")

    def scavenge_wheat(self):
        """
        Scans for and attempts to pick up wheat until Grain is in the inventory
        """
        while not self.api_morg.get_if_item_in_inv(item_ids.GRAIN):
            wheat_objects = self.get_all_tagged_in_rect(self.win.game_view, ObjectColors.WHEAT)
            self.mouse.move_to(wheat_objects[0].random_point())
            self.mouse.right_click()
            if pick_option := ocr.find_text(["Pick"], self.win.game_view, ocr.BOLD_12, clr.WHITE):
                self.mouse.move_to(pick_option[0].random_point())
                self.mouse.click()
                self.wait_until_idle()
            else:
                cancel_option = ocr.find_text("Cancel", self.win.game_view, ocr.BOLD_12, clr.WHITE)
                self.mouse.move_to(cancel_option[0].random_point())
                self.mouse.click()
            time.sleep(1)
        self.log_msg("Got the wheat!")

    def operate_hopper(self):
        hopper = self.get_all_tagged_in_rect(self.win.game_view, ObjectColors.HOPPER)
        self.mouse.move_to(self.win.cp_tabs[3].random_point())  # Select inv
        grain_indices = self.api_morg.get_inv_item_indices(item_ids.GRAIN)

        grain_slot = self.win.inventory_slots[grain_indices[0]]

        self.mouse.move_to(grain_slot.random_point())
        self.mouse.click()
        self.mouse.move_to(hopper[0].random_point())
        self.mouse.right_click()
        if use_option := ocr.find_text(["Use"], self.win.game_view, ocr.BOLD_12, clr.WHITE):
            self.mouse.move_to(use_option[0].random_point())
            if self.mouse.click(check_red_click=True):
                self.log_msg("Used grain on hopper")
        else:
            self.log_msg("No use option on hopper!")
            self.stop()

        self.wait_until_idle()

        hopper_controls = self.get_all_tagged_in_rect(self.win.game_view, ObjectColors.HOPPER_CONTROLS)
        self.mouse.move_to(hopper_controls[0].random_point())
        if self.mouse.click(check_red_click=True):
            self.log_msg("Used hopper controls")
        self.wait_until_idle()

    def empty_flour_bin(self):
        flour_bin = self.get_all_tagged_in_rect(self.win.game_view, ObjectColors.FLOUR_BIN)
        self.mouse.move_to(flour_bin[0].random_point())
        if self.mouse.click(check_red_click=True):
            self.log_msg("Emptying flour bin")
        self.wait_until_idle()

    def milk_cow(self):
        dairy_cow = self.get_all_tagged_in_rect(self.win.game_view, ObjectColors.DAIRY_COW)
        self.mouse.move_to(dairy_cow[0].random_point())
        self.mouse.right_click()
        if milk_option := ocr.find_text(["Milk"], self.win.game_view, ocr.BOLD_12, clr.WHITE):
            self.mouse.move_to(milk_option[0].random_point())
            self.mouse.click()
        else:
            self.log_msg("No use option on hopper!")
            self.stop()

        self.wait_until_idle()

    def appease_cook(self):
        cook = self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN)

        # Get in dialogue
        while True:
            self.mouse.move_to(cook[0].random_point())
            self.mouse.right_click()
            if talk_option := ocr.find_text("Talk-to", self.win.game_view, ocr.BOLD_12, clr.WHITE):
                self.mouse.move_to(talk_option[0].random_point())
                self.mouse.click()
                self.wait_until_idle()
                break
            else:
                cancel_option = ocr.find_text("Cancel", self.win.game_view, ocr.BOLD_12, clr.WHITE)
                self.mouse.move_to(cancel_option[0].random_point())
                self.mouse.click()
                continue

        self.continue_dialog()

        self.press_keyboard_key("num1")
        time.sleep(DelayTicks.TWO)

        self.continue_dialog()

        self.press_keyboard_key("num1")

    def continue_dialog(self):
        while ocr.find_text(["Click here to continue", "Please wait..."], self.win.chat, ocr.QUILL_8, clr.BLUE):
            self.press_keyboard_key("space")
            time.sleep(DelayTicks.TWO)

    def wait_until_idle(self, delay: DelayTicks = DelayTicks.ONE):
        while not self.api_morg.get_is_player_idle():
            self.log_msg("Not idle yet")
            time.sleep(0.2)
        time.sleep(delay)

    def walk_here(self):
        # TODO Right click, Walk Here, to avoid combat / red Xs
        self.mouse.click()
        pass


# TODO Load Color with hex
class ObjectColors(NamedTuple):
    DOOR = clr.Color([255, 0, 231])
    WHEAT = clr.Color([255, 10, 0])
    LADDER = clr.Color([250, 255, 0])
    FLOUR_BIN = clr.Color([255, 0, 67])
    DAIRY_COW = clr.Color([255, 77, 0])
    HOPPER = clr.Color([255, 154, 0])
    HOPPER_CONTROLS = clr.Color([255, 77, 0])
