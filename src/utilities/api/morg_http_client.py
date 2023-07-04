"""
API utility for MorgHTTPClient socket plugin.
"""
import time
from typing import List, Tuple, Union

import requests
from deprecated import deprecated
from requests.exceptions import ConnectionError


class SocketError(Exception):
    def __init__(self, error_message: str, endpoint: str):
        self.__error_message = error_message
        self.__endpoint = endpoint
        super().__init__(self.get_error())

    def get_error(self):
        return f"{self.__error_message} endpoint: {self.__endpoint}"


class MorgHTTPSocket:
    def __init__(self):
        self.base_endpoint = "http://localhost:8081/"

        self.inv_endpoint = "inv"
        self.stats_endpoint = "stats"
        self.equip_endpoint = "equip"
        self.events_endpoint = "events"

        self.timeout = 1

    def __do_get(self, endpoint: str) -> dict:
        """
        Args:
                endpoint: One of either "inv", "stats", "equip", "events"
        Returns:
                All JSON data from the endpoint as a dict.
        Raises:
                SocketError: If the endpoint is not valid or the server is not running.
        """
        try:
            response = requests.get(f"{self.base_endpoint}{endpoint}", timeout=self.timeout)
        except ConnectionError as e:
            raise SocketError("Unable to reach socket", endpoint) from e

        if response.status_code != 200:
            if response.status_code == 204:
                return {}
            else:
                raise SocketError(
                    f"Unable to reach socket. Status code: {response.status_code}",
                    endpoint,
                )

        return response.json()

    def test_endpoints(self) -> bool:
        """
        Ensures all endpoints are working correctly to avoid errors happening when any method is called.
        Returns:
                True if successful, False otherwise.
        """
        for i in list(self.__dict__.values())[1:-1]:  # Look away
            try:
                self.__do_get(endpoint=i)
            except SocketError as e:
                print(e)
                print(f"Endpoint {i} is not working.")
                return False
        return True

    def get_hitpoints(self) -> Tuple[int, int]:
        """
        Fetches the current and maximum hitpoints of the player.
        Returns:
                A Tuple(current_hitpoints, maximum_hitpoints).
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        if hitpoints_data := data.get("health"):
            cur_hp, max_hp = hitpoints_data.split("/")
            return int(cur_hp), int(max_hp)
        else:
            return -1, -1

    def get_run_energy(self) -> int:
        """
        Fetches the current run energy of the player.
        Returns:
                An int representing the current run energy.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return int(run_energy) if (run_energy := data.get("run energy")) else -1

    def get_animation(self) -> int:
        """
        Fetches the current animation the actor is performing.
        Returns:
                An int representing the current animation.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return int(data["animation"]) if data.get("animation") else -1

    def get_animation_id(self) -> int:
        """
        Fetches the current animation frame ID the actor is using. Useful for checking if the player is doing
        a particular action.
        Returns:
                An int representing the current animation ID.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return int(data["animation pose"]) if data.get("animation pose") else -1

    def get_is_player_idle(self, poll_seconds=1) -> bool:
        """
        Checks if the player is doing an idle animation.
        Args:
                poll_seconds: The number of seconds to poll for an idle animation.
        Returns:
                True if the player is idle, False otherwise..
        """
        start_time = time.time()
        while time.time() - start_time < poll_seconds:
            data = self.__do_get(endpoint=self.events_endpoint)
            if data.get("animation") != -1 or data.get("animation pose") not in [808, 813]:
                return False
        return True

    def get_skill_level(self, skill: str) -> int:
        # sourcery skip: class-extract-method
        """
        Gets level of inputted skill.
        Args:
                skill: the name of the skill (not case sensitive)
        Returns:
                The level of the skill as an int, or -1 if an error occurred.
        """
        data = self.__do_get(endpoint=self.stats_endpoint)
        try:
            level = next(int(i["level"]) for i in data[1:] if i["stat"] == skill)
        except StopIteration:
            print(f"Invalid stat name: {skill}. Consider using the `stat_names` utility.")
            return -1
        return level

    def get_skill_xp(self, skill: str) -> int:
        """
        Gets the total xp of a skill.
        Args:
                skill: the name of the skill.
        Returns:
                The total xp of the skill as an int, or -1 if an error occurred.
        """
        data = self.__do_get(endpoint=self.stats_endpoint)
        try:
            total_xp = next(int(i["xp"]) for i in data[1:] if i["stat"] == skill)
        except StopIteration:
            print(f"Invalid stat name: {skill}. Consider using the `stat_names` utility.")
            return -1
        return total_xp

    def get_skill_xp_gained(self, skill: str) -> int:
        """
        Gets the xp gained of a skill. The tracker begins at 0 on client startup.
        Args:
                skill: the name of the skill.
        Returns:
                The xp gained of the skill as an int, or -1 if an error occurred.
        """
        data = self.__do_get(endpoint=self.stats_endpoint)
        try:
            xp_gained = next(int(i["xp gained"]) for i in data[1:] if i["stat"] == skill)
        except StopIteration:
            print(f"Invalid stat name: {skill}. Consider using the `stat_names` utility.")
            return -1
        return xp_gained

    def wait_til_gained_xp(self, skill: str, timeout: int = 10) -> int:
        """
        Waits until the player has gained xp in the inputted skill.
        Args:
                skill: the name of the skill (not case sensitive).
                timeout: the maximum amount of time to wait for xp gain (seconds).
        Returns:
                The xp gained of the skill as an int, or -1 if no XP was gained or an error occurred during the timeout.
        """
        starting_xp = self.get_skill_xp(skill)
        if starting_xp == -1:
            print("Failed to get starting xp.")
            return -1

        stop_time = time.time() + timeout
        while time.time() < stop_time:
            data = self.__do_get(endpoint=self.stats_endpoint)
            final_xp = next(int(i["xp"]) for i in data[1:] if i["stat"] == skill)
            if final_xp > starting_xp:
                return final_xp
            time.sleep(0.2)
        return -1

    def get_game_tick(self) -> int:
        """
        Fetches game tick number.
        Returns:
                An int representing the current game tick.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return int(data["game tick"]) if "game tick" in data else -1

    def get_latest_chat_message(self) -> str:
        """
        Fetches the most recent chat message in the chat box.
        Returns:
                A string representing the latest chat message.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return data["latest msg"] if "latest msg" in data else ""

    def get_player_position(self) -> Tuple[int, int, int]:
        """
        Fetches the world point of a player.
        Returns:
                A tuple of ints representing the player's world point (x, y, z), or (-1, -1, -1) if data is not present or invalid.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        if "worldPoint" not in data:
            return -1, -1, -1
        return (
            int(data["worldPoint"]["x"]),
            int(data["worldPoint"]["y"]),
            int(data["worldPoint"]["plane"]),
        )

    def get_player_region_data(self) -> Tuple[int, int, int]:
        """
        Fetches region data of a player's position.
        Returns:
                A tuple of ints representing the player's region data (region_x, region_y, region_ID).
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        if "worldPoint" not in data:
            return -1, -1, -1
        return (
            int(data["worldPoint"]["regionX"]),
            int(data["worldPoint"]["regionY"]),
            int(data["worldPoint"]["regionID"]),
        )

    def get_camera_position(self) -> Union[dict, None]:
        """
        Fetches the position of a player's camera.
        Returns:
                A dict containing the player's camera position {yaw, pitch, x, y, z, x2, y2, z2},
                or None if data is not present or invalid.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return data["camera"] if "camera" in data else None

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Fetches the position of a player's mouse.
        Returns:
                A tuple of ints representing the player's mouse position (x, y).
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        if "mouse" not in data:
            return -1, -1
        return int(data["mouse"]["x"]), int(data["mouse"]["y"])

    def get_interaction_code(self) -> str:
        """
        Fetches the interacting code of the current interaction. (Use case unknown)
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return data["interacting code"] if "interacting code" in data else None

    def get_is_in_combat(self) -> Union[bool, None]:
        """
        Determines if the player is in combat.
        Returns:
                True if the player is in combat, False if not.
                Returns None if an error occurred.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return None if "npc name" not in data else data["npc name"] != "null"

    @deprecated(reason="This method seems to return unreliable values for the NPC's HP.")
    def get_npc_hitpoints(self) -> Union[int, None]:
        """
        Fetches the HP of the NPC currently targetted.
        TODO: Result seems to be multiplied by 6...?
        Returns:
                An int representing the NPC's HP, or None if an error occurred.
                If no NPC is in combat, returns 0.
        """
        data = self.__do_get(endpoint=self.events_endpoint)
        return int(data["npc health "])

    def get_inv(self):
        """
        Gets a list of dicts representing the player inventory.
        Returns:
            List of dictionaries, each containing index, ID, and quantity of an item.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        inventory = []
        for index, item in enumerate(data):
            if item["quantity"] == 0:
                continue
            item_info = {"index": index, "id": item["id"], "quantity": item["quantity"]}
            inventory.append(item_info)
        return inventory

    def get_if_item_in_inv(self, item_id: Union[List[int], int]) -> bool:
        """
        Checks if an item is in the inventory or not.
        Args:
                item_id: the id of the item to check for (an single ID, or list of IDs).
        Returns:
                True if the item is in the inventory, False if not.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if isinstance(item_id, int):
            return any(inventory_slot["id"] == item_id for inventory_slot in data)
        elif isinstance(item_id, list):
            return any(inventory_slot["id"] in item_id for inventory_slot in data)

    def get_is_inv_full(self) -> bool:
        """
        Checks if player's inventory is full.
        Returns:
                True if the player's inventory is full, False otherwise.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        return len([item["id"] for item in data if item["id"] != -1]) == 28

    def get_is_inv_empty(self) -> bool:
        """
        Checks if player's inventory is empty.
        Returns:
                True if the player's inventory is empty, False otherwise.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        return not [item["id"] for item in data if item["id"] != -1]

    def get_inv_item_indices(self, item_id: Union[List[int], int]) -> list:
        """
        For the given item ID(s), returns a list of inventory slot indexes that the item exists in.
        Useful for locating items you do not want to drop. If you want to locate an item in your
        inventory, consider using :meth:`MorgHTTPSocket.get_first_occurrence()` instead.
        Args:
                item_id: The item ID to search for (an single ID, or list of IDs).
        Returns:
                A list of inventory slot indexes that the item(s) exists in.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if isinstance(item_id, int):
            return [i for i, inventory_slot in enumerate(data) if inventory_slot["id"] == item_id]
        elif isinstance(item_id, list):
            return [i for i, inventory_slot in enumerate(data) if inventory_slot["id"] in item_id]

    def get_first_occurrence(self, item_id: Union[List[int], int]) -> Union[int, List[int]]:
        """
        For the given item ID(s), returns the first inventory slot index that the item exists in.
        e.g. [1, 1, 2, 3, 3, 3, 4, 4, 4, 4] -> [0, 2, 3, 6]
        Args:
            item_id: The item ID to search for (an single ID, or list of IDs).
        Returns:
            The first inventory slot index that the item exists in for each unique item ID.
            If a single item ID is provided, returns an integer (or -1).
            If a list of item IDs is provided, returns a list of integers (or empty list).
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if isinstance(item_id, int):
            return next((i for i, inventory_slot in enumerate(data) if inventory_slot["id"] == item_id), -1)
        elif isinstance(item_id, list):
            first_occurrences = {}
            for i, inventory_slot in enumerate(data):
                item_id_in_slot = inventory_slot["id"]
                if item_id_in_slot not in first_occurrences and item_id_in_slot in item_id:
                    first_occurrences[item_id_in_slot] = i
            return list(first_occurrences.values())

    def get_inv_item_stack_amount(self, item_id: Union[int, List[int]]) -> int:
        """
        For the given item ID, returns the total amount of that item in your inventory.
        This is only useful for items that stack (e.g. coins, runes, etc).
        Args:
            id: The item ID to search for. If a list is passed, the first matching item will be used.
                This is useful for items that have multiple IDs (e.g. coins, coin pouches, etc.).
        Returns:
            The total amount of that item in your inventory.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if isinstance(item_id, int):
            item_id = [item_id]
        if result := next((item for item in data if item["id"] in item_id), None):
            return int(result["quantity"])
        return 0

    def get_is_item_equipped(self, item_id: Union[int, List[int]]) -> bool:
        """
        Checks if the player has given item(s) equipped. Given a list of IDs, returns True on first ID found.
        Args:
                item_id: the id of the item to check for (a single ID, or list of IDs).
        Returns:
                True if an item is equipped, False if not.
        """
        data = self.__do_get(endpoint=self.equip_endpoint)
        equipped_ids = [item["id"] for item in data]
        if isinstance(item_id, int):
            return item_id in equipped_ids
        return any(item in item_id for item in equipped_ids)

    def get_equipped_item_quantity(self, item_id: int) -> int:
        """
        Checks for the quantity of an equipped item.
        Args:
                item_id: The ID of the item to check for.
        Returns:
                The quantity of the item equipped, or 0 if not equipped.
        """
        data = self.__do_get(endpoint=self.equip_endpoint)
        return next(
            (int(equip_slot["quantity"]) for equip_slot in data if equip_slot["id"] == item_id),
            0,
        )

    def convert_player_position_to_pixels(self):
        """
        Convert a world point into coordinate where to click with the mouse to make it possible to move via the socket.
        TODO: Implement.
        """
        pass


# sourcery skip: remove-redundant-if
if __name__ == "__main__":
    import item_ids as ids

    api = MorgHTTPSocket()

    # Note: Making API calls in succession too quickly can result in issues
    while True:
        # Player Data
        if False:
            # Example of safely getting player data
            if hp := api.get_hitpoints():
                print(f"Current HP: {hp[0]}")
                print(f"Max HP: {hp[1]}")

            print(f"Run Energy: {api.get_run_energy()}")
            print(f"get_animation(): {api.get_animation()}")
            print(f"get_animation_id(): {api.get_animation_id()}")
            print(f"Is player idle: {api.get_is_player_idle()}")

        # World Data
        if False:
            print(f"Game tick: {api.get_game_tick()}")
            print(f"Player position: {api.get_player_position()}")
            print(f"Player region data: {api.get_player_region_data()}")
            print(f"Mouse position: {api.get_mouse_position()}")
            # print(f"get_interaction_code(): {api.get_interaction_code()}")
            print(f"Is in combat?: {api.get_is_in_combat()}")
            print(f"get_npc_health(): {api.get_npc_hitpoints()}")

        # Inventory Data
        if False:
            print(f"Is inventory full: {api.get_is_inv_full()}")
            print(f"Is inventory empty: {api.get_is_inv_empty()}")
            print(f"Are logs in inventory?: {api.get_if_item_in_inv(ids.logs)}")
            print(f"Find amount of change in inv: {api.get_inv_item_stack_amount(ids.coins)}")
            print(f"Get position of all bones in inv: {api.get_inv_item_indices(ids.BONES)}")
            print(f"Get position of first logs in inventory: {api.get_first_occurrence(ids.LOGS)}")

        # Wait for XP to change
        if False:
            print(f"WC Level: {api.get_skill_level('Woodcutting')}")
            print(f"WC XP: {api.get_skill_xp('Woodcutting')}")
            print(f"WC XP Gained: {api.get_skill_xp_gained('Woodcutting')}")
            print("---waiting for wc xp to be gained---")
            if api.wait_til_gained_xp(skill="Woodcutting", timeout=10):
                print("Gained xp!")
            else:
                print("No xp gained.")

        # Equipment Data
        if False:
            print(f"Is bronze axe equipped?: {api.get_is_item_equipped(ids.BRONZE_AXE)}")
            print(f"Are there any ring of duelings equipped? {api.get_is_item_equipped(ids.rods)}")
            print(f"How many bronze arrows equipped?: {api.get_equipped_item_quantity(ids.BRONZE_ARROW)}")

        # Chatbox Data
        if True:
            print(f"Latest chat message: {api.get_latest_chat_message()}")

        time.sleep(2)

        print("\n--------------------------\n")
