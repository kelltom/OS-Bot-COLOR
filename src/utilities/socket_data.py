from requests.exceptions import ConnectionError
from typing import List, Union, Tuple
import requests
import time


class SocketError:
	def __init__(self, error_message: str, endpoint: str):
		self.__error_message = error_message
		self.__endpoint = endpoint

	def get_error(self):
		return f"{self.__error_message} endpoint: {self.__endpoint}"


class Socket:

	# TODO: ID/NPC ID/Object ID conversion function/dict to get the readable name of an object

	def __init__(self):
		self.base_endpoint = "http://localhost:8081/"

		self.inv_endpoint = "inv"
		self.stats_endpoint = "stats"
		self.equip_endpoint = "equip"
		self.events_endpoint = "events"

		self.timeout = 1

	# TODO: Ensure properties contains runelite.externalPlugins=morghttpclient

	def do_get(self, endpoint: str) -> Union[dict, SocketError]:
		"""

		Args:
			endpoint: One of either "inv", "stats", "equip", "events"

		Returns:
			All JSON data from the endpoint as a dict.
			If an error occurs it will return a SocketError
		"""

		try:
			response = requests.get(f"{self.base_endpoint}{endpoint}", timeout=self.timeout)
		except ConnectionError:
			return SocketError(f"Unable to reach socket", endpoint)

		if response.status_code != 200:
			if response.status_code == 204:
				return SocketError(
					f"Endpoint not available, make sure you are fully logged in, status code: {response.status_code}",
					endpoint)
			else:
				return SocketError(f"Unable to reach socket, status code: {response.status_code}", endpoint)

		return response.json()

	def __get_stats(self) -> Union[dict, SocketError]:
		"""
		Gets all the data from the stats endpoint
		Returns:

		"""
		stats_data = self.do_get(endpoint=self.stats_endpoint)
		return stats_data

	def __get_equipped(self) -> Union[dict, SocketError]:
		"""
		Gets all the data from the equip endpoint
		Returns:

		"""
		equipped_data = self.do_get(endpoint=self.equip_endpoint)
		return equipped_data

	def __get_inventory(self) -> Union[dict, SocketError]:
		"""
		Gets all the data from the inventory endpoint

		Returns:

		"""
		inventory_data = self.do_get(endpoint=self.inv_endpoint)
		return inventory_data

	def __get_events(self) -> Union[dict, SocketError]:
		"""
		Returns: All event data including animation, game ticks, health, positions, run energy etc

		"""
		event_data = self.do_get(endpoint=self.events_endpoint)
		return event_data

	def __test_endpoints(self) -> bool:
		"""
		Ensures all endpoints are working correctly to avoid errors happening when any method is called

		Returns: True if successful False otherwise

		"""
		for i in list(self.__dict__.values())[1:-1]:  # Look away
			test_endpoint = self.do_get(endpoint=i)
			if isinstance(test_endpoint, SocketError):
				print(f"SOCKET FAILURE: {test_endpoint.get_error()}")
				return False

		return True

	def get_hitpoints(self) -> Union[SocketError, Tuple[int, int]]:
		"""

		Returns: SocketError, tuple(current_hitpoints, maximum_hitpoints)

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		hitpoints_data = data['health']
		cur_hp, max_hp = hitpoints_data.split("/")  # hitpoints_data example = "21/21"
		return int(cur_hp), int(max_hp)

	def run_energy(self) -> Union[SocketError, int]:
		"""

		Returns: SocketError, tuple(current_hitpoints, maximum_hitpoints)

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['run energy'])

	def get_animation(self) -> Union[SocketError, int]:
		"""
		Not sure what this data is used for
		Returns: SocketError, Current animation ID.

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['animation'])

	def get_animation_id(self) -> Union[SocketError, int]:
		"""
		Allows for making custom conditions based on animation ID (mining, woodcutting, etc).
		Returns: SocketError, Current animation ID.

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['animation pose'])

	def get_is_player_idle(self) -> Union[SocketError, bool]:
		"""
		Checks the animation ID to see if the player is standing still.
		Could be used for waiting for the player to stop after an action.

		Returns: SocketError, True if the player is running, false otherwise

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		animation_id = data['animation pose']

		if animation_id in [808, 813]:  # TODO: These are idle animations but there may be more
			return True

		return False

	def get_stat_level(self, stat_name: str) -> Union[SocketError, str, int]:
		"""
		Gets level of inputted stat
		Args:
			stat_name: the name of the stat (not case sensitive)

		Returns: SocketError, str if invalid stat_name, int as level

		"""
		# TODO: Make class for stat_names to make invalid names impossible
		stat_name = stat_name.lower().capitalize()  # Ensures str is formatted correctly for socket json key
		data = self.__get_stats()
		if isinstance(data, SocketError):
			return data

		try:
			level = next(int(i['level']) for i in data[1:] if i['stat'] == stat_name)
		except StopIteration:
			return "Invalid Stat Name"

		return level

	def get_stat_xp(self, stat_name: str) -> Union[SocketError, str, int]:
		"""
		Gets the total XP of a stat
		Args:
			stat_name: the name of the stat (not case sensitive)

		Returns: SocketError, str if invalid stat_name, int as xp

		"""
		stat_name = stat_name.lower().capitalize()  # Ensures str is formatted correctly for socket json key
		data = self.__get_stats()
		if isinstance(data, SocketError):
			return data

		try:
			total_xp = next(int(i['xp']) for i in data[1:] if i['stat'] == stat_name)
		except StopIteration:
			return "Invalid Stat Name"

		return total_xp

	def get_stat_xp_gained(self, stat_name: str) -> Union[SocketError, str, int]:
		"""
		Gets the XP gained of a stat, tracker is started at 0 on client startup
		Args:
			stat_name: the name of the stat (not case sensitive)

		Returns: SocketError, str if invalid stat_name, int as xp gained

		"""
		stat_name = stat_name.lower().capitalize()  # Ensures str is formatted correctly for socket json key
		data = self.__get_stats()
		if isinstance(data, SocketError):
			return data

		try:
			xp_gained = next(int(i['xp gained']) for i in data[1:] if i['stat'] == stat_name)
		except StopIteration:
			return "Invalid Stat Name"

		return xp_gained

	def wait_til_gained_xp(
			self,
			stat_name: str,
			starting_xp: int,
			wait_time: int = 1
	) -> Union[SocketError, int, None]:
		"""
			Waits until the player as gained XP
			Args:
				stat_name: the name of the stat (not case sensitive)
				starting_xp: The current XP of the player.
				wait_time: This is how long (in seconds) the function will wait to check for XP, 1 by default

			Returns: SocketError, int of new XP value, None if no XP is gained

		"""

		stat_name = stat_name.lower().capitalize()  # Ensures str is formatted correctly for socket json key
		stop_time = time.time() + wait_time
		while time.time() < stop_time:

			data = self.__get_equipped()
			if isinstance(data, SocketError):
				return data

			xp_gained = next(int(i['xp']) for i in data[1:] if i['stat'] == stat_name)
			if xp_gained > starting_xp:
				return xp_gained

		return None

	def get_game_tick(self) -> Union[SocketError, int]:
		"""

		Returns: SocketError, game tick #

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		game_tick = int(data['game tick'])
		return game_tick

	def get_player_position(self) -> Union[SocketError, Tuple[int, int, int]]:
		"""
		Gets the world point of a player
		Returns: SocketError, Tuple(x, y, z)

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data
		return int(data['worldPoint']['x']), int(data['worldPoint']['y']), int(data['worldPoint']['plane'])

	def get_player_region_data(self) -> Union[SocketError, Tuple[int, int, int]]:
		"""
		Gets the region data of a players position
		Returns: SocketError, Tuple(region_x, region_y, region_ID)

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['worldPoint']['regionX']), int(data['worldPoint']['regionY']), int(
			data['worldPoint']['regionID'])

	def get_camera_position(self) -> Union[SocketError, dict]:
		"""
		Gets the position of a players camera
		Returns: SocketError, dict containing, yaw, pitch, x, y, z, x2, y2, z2

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return data['camera']

	def get_mouse_position(self) -> Union[SocketError, Tuple[int, int]]:
		"""
		Gets the position of a players mouse
		Returns: SocketError, tuple(x, y)

		"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['mouse']['x']), int(data['mouse']['y'])

	def get_interaction_code(self) -> Union[SocketError, int]:
		"""Not sure what the use case of this code is atm"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['interacting code'])

	def get_npc_name(self) -> Union[SocketError, int]:
		"""Not sure what the use case of this code is atm"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['npc name'])

	def get_npc_health(self) -> Union[SocketError, int]:
		"""Not sure what the use case of this code is atm"""
		data = self.__get_events()
		if isinstance(data, SocketError):
			return data

		return int(data['npc health'])

	def get_if_item_in_inv(self, item_id: int) -> Union[SocketError, bool]:
		"""
		Get's if an item is in the inventory or not
		Args:
			item_id: the id of the item

		Returns: SocketError, True/False

		"""
		data = self.__get_inventory()
		if isinstance(data, SocketError):
			return data

		for inventory_slot in data:
			if inventory_slot['id'] == item_id:
				return True

		return False

	def find_item_in_inv(self, item_id: int) -> Union[SocketError, List[Tuple[int, int]]]:
		"""
		Finds the item is in the inventory and returns a list of tuples containing the index and quantity
		Args:
			item_id: The ID of the item

		Returns: SocketError, [(index, quantity),]

		"""
		data = self.__get_inventory()
		if isinstance(data, SocketError):
			return data

		item_found = list()
		for index, inventory_slot in enumerate(data):
			if inventory_slot['id'] == item_id:
				item_found.append((index, inventory_slot['quantity']))

		return item_found

	def get_player_equipment(self) -> Union[SocketError, List[int]]:
		"""
		Currently just gets the ID of the equipment until there is an easier way to convert ID to readable name
		-1 = nothing
		Returns: [helmet, cape, neck, weapon, chest, shield, legs, gloves, boots, ring, arrow]

		NOTE: Socket may be bugged with -1's in the middle of the data even all equipment slots are filled
		"""
		data = self.__get_equipped()
		if isinstance(data, SocketError):
			return data

		return [equipment_id['id'] for equipment_id in data]

	def convert_player_position_to_pixels(self):
		"""
		Convert a world point into coordinate where to click with the mouse to make it possible to move via the socket.
		Returns:

		"""
		...
