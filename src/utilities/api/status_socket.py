"""
Requires the Status Socket plugin in RuneLite. Endpoint: "http://localhost:5000".
"""
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import List, Union

import simplejson as JSON

# Global to store the data returned from sockets plugin
player_data = {}


# Http request handler class to handle receiving data from the status socket
class RLSTATUS(BaseHTTPRequestHandler):
    data_bytes: bytes

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        global player_data
        self._set_headers()
        self.data_bytes = self.rfile.read(int(self.headers["Content-Length"]))
        self.send_response(200)
        self.end_headers()
        player_data = JSON.loads(self.data_bytes)

    def log_message(self, format, *args):
        """
        Suppress logging.
        """
        return


class StatusSocket:
    gameTick = 0.603

    def __init__(self) -> None:
        t_server = Thread(target=self.__RSERVER)
        t_server.daemon = True
        t_server.start()
        print("thread alive:", t_server.is_alive())

    def __RSERVER(self, port=5000):
        try:
            httpd = HTTPServer(("127.0.0.1", port), RLSTATUS)
            httpd.serve_forever()
        except OSError:
            print("Status socket already running.")

    def get_player_data(self):
        """
        Fetches the entire blob of player_Data
        """
        print(player_data)
        return player_data

    def get_game_tick(self) -> int:
        """
        Fetches the game tick from the API.
        """
        return player_data["tick"]

    def get_real_level(self, skill_name):
        """
        Fetches the real level of a skill.
        Args:
            skill_name: The name of the skill to check (must be all caps).
        Example:
            >>> print(api_status.get_real_level("ATTACK"))
        """
        return next(
            (skill["realLevel"] for skill in player_data["skills"] if skill["skillName"] == skill_name),
            None,
        )

    def get_boosted_level(self, skill_name):
        """
        Fetches boosted level of a skill.
        Args:
            skill_name: The name of the skill to check (must be all caps).
        Example:
            >>> print(api_status.get_boosted_level("ATTACK"))
        """
        return next(
            (skill["boostedLevel"] for skill in player_data["skills"] if skill["skillName"] == skill_name),
            None,
        )

    def get_is_boosted(self, skill_name) -> bool:
        """
        Compares real level to boosted level of a skill.
        Args:
            skill_name: The name of the skill to check (must be all caps).
        Returns:
            True if boosted level is greater than real level
        Example:
            >>> print(api_status.get_is_boosted("ATTACK"))
        """
        real_level = self.get_real_level(skill_name)
        boosted_level = self.get_boosted_level(skill_name)
        if real_level is not None and boosted_level is not None:
            return boosted_level > real_level
        return False

    def get_run_energy(self) -> int:
        """
        Gets the player's current run energy.
        Returns:
                The player's current run energy as an int.
        """
        return int(player_data["runEnergy"])

    def get_is_inv_full(self) -> bool:
        """
        Checks if player's inventory is full.
        Returns:
                True if the player's inventory is full, False otherwise.
        """
        return len(player_data["inventory"]) >= 28

    def get_is_inv_empty(self) -> bool:
        """
        Checks if player's inventory is empty.
        Returns:
                True if the player's inventory is empty, False otherwise.
        """
        return len(player_data["inventory"]) == 0

    def get_inv(self) -> list:
        """
        Gets a list of dicts representing the player inventory.
        Returns:
                A list of dicts with the following keys:
                        - index: The position of the item in the inventory.
                        - id: The item ID.
                        - quantity: The quantity of the item.
        Example:
                for item in inv:
                        print(f"Slot: {item['index']}, Item ID: {item['id']}, Amount: {item['amount']}")
        """
        return player_data["inventory"]

    def get_inv_item_indices(self, item_id: Union[List[int], int]) -> list:
        """
        For the given item ID, returns a list of inventory slot indexes that the item exists in.
        Useful for locating items you do not want to drop.
        Args:
                item_id: The item ID to search for (an single ID, or list of IDs).
        Returns:
                A list of inventory slot indexes that the item exists in.
        """
        inv = player_data["inventory"]
        if isinstance(item_id, int):
            return [slot["index"] for slot in inv if slot["id"] == item_id]
        elif isinstance(item_id, list):
            return [slot["index"] for slot in inv if slot["id"] in item_id]

    def get_inv_item_stack_amount(self, item_id: Union[int, List[int]]) -> int:
        """
        For the given item ID, returns the total amount of that item in your inventory.
        This is only useful for items that stack (e.g. coins, runes, etc).
        Args:
                item_id: The item ID to search for. If a list is passed, the first matching item will be used.
                         This is useful for items that have multiple IDs (e.g. coins, coin pouches, etc.).
        Returns:
                The total amount of that item in your inventory.
        """
        inv = player_data["inventory"]
        if isinstance(item_id, int):
            item_id = [item_id]
        if result := next((item for item in inv if item["id"] in item_id), None):
            return int(result["amount"])
        return 0

    def get_is_player_idle(self) -> bool:
        """
        Checks if the player is idle. Note, this does not check if the player is moving - it only
        checks if they are performing an action animation (skilling, combat, etc).
        Returns:
                True if the player is idle, False otherwise.
        Notes:
                If you have the option, use MorgHTTPClient's idle check function instead. This one
                does not consider movement animations.
        """
        # run a loop for 0.6 second
        start_time = time.time()
        while time.time() - start_time < 0.8:
            if player_data["attack"]["animationId"] != -1:
                return False
        return True

    def get_is_player_praying(self) -> bool:
        """
        Checks if the player is currently praying. Useful for knowing when you've run out of prayer points.
        Returns:
                True if the player is praying, False otherwise.
        """
        return bool(player_data["prayers"])

    def get_player_equipment(self) -> list:
        return player_data["equipment"] or []

    # pass; returns a list of stats like stab, slash, crush, will return all 0s if nothing is worn
    def get_equipment_stats(self) -> list:
        """
        Checks your current equipment stats. Includes aStab, aSlash, aCrush, aMagic, aRange,
        dStab, dSlash, dCrush, dMagic, dRange, str, rStr, mDmg.
        Returns:
                A list of your current equipment stats.
        """
        return player_data["equipmentStats"]

    def get_animation_data(self) -> list:
        return (
            player_data["attack"]["animationName"],
            player_data["attack"]["animationId"],
            player_data["attack"]["animationIsSpecial"],
            player_data["attack"]["animationBaseSpellDmg"],
        )

    def get_animation_id(self) -> int:
        return player_data["attack"]["animationId"]


# Test Code
if __name__ == "__main__":
    print("Attempting to start server...")
    api = StatusSocket()

    while True:
        # api.get_PlayerData()
        time.sleep(api.gameTick)
        print(f"Real Strength Level: {api.get_real_level('STRENGTH')}")
        print(f"Boosted Strength Level: {api.get_boosted_level('STRENGTH')}")
        print(f"Is Strength boosted?: {api.get_is_boosted('STRENGTH')}")
        print(f"Run Energy: {api.get_run_energy()}")
        print(f"Is Inventory Full: {api.get_is_inv_full()}")
        print(f"Inventory: {api.get_inv()}")
        print(f"Indexes of bones and chickens in inventory: {api.get_inv_item_indices([526, 2138])}")
        print(f"Indexs of bones in inventory: {api.get_inv_item_indices(526)}")
        print(f"Is Player Praying: {api.get_is_player_praying()}")
        print(f"Player Equipment: {api.get_player_equipment()}")
        print(f"Equipment Stats: {api.get_equipment_stats()}")
        print(f"Is Player Idle: {api.get_is_player_idle()}")
        print(f"Animation Data: {api.get_animation_data()}")
        print(f"Animation ID: {api.get_animation_id()}")

        print("-----------------------------")
