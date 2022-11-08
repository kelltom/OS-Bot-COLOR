from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Union, List
import simplejson as JSON
import time

# Requires the status socket plugin in RuneLite. Install and then click on the settings for it and add port 5000. "http://localhost:5000"
# Global to store the data returned from sockets plugin
player_Data = {}

# Http request handler class to handle receiving data from the status socket
class RLSTATUS(BaseHTTPRequestHandler):
	data_bytes: bytes

	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_POST(self):
		global player_Data
		self._set_headers()
		self.data_bytes = self.rfile.read(int(self.headers['Content-Length']))
		self.send_response(200)
		self.end_headers()
		player_Data = JSON.loads(self.data_bytes)
	
	def log_message(self, format, *args):
		'''
		Suppress logging.
		'''
		return

class API():

	gameTick = 0.603

	def __init__(self) -> None:
		t_server = Thread(target=self.__RSERVER)
		t_server.daemon = True
		t_server.start()
		print('thread alive:', t_server.is_alive())
	
	def __RSERVER(self, port=5000):
		httpd = HTTPServer(('127.0.0.1', port), RLSTATUS)
		httpd.serve_forever()

	def get_PlayerData(self):
		'''
		Fetches the entire blob of player_Data
		'''
		print(player_Data)
		return player_Data
	
	def get_GameTick(self) -> int:
		'''
		Fetches the game tick from the API.
		'''
		return player_Data["tick"]
	
	def get_PlayerRunEnergy(self) -> int:
		'''
		Gets the player's current run energy.
		Returns:
			The player's current run energy as an int.
		'''
		return int(player_Data["runEnergy"])

	def get_IsInventoryFull(self) -> bool:
		'''
		Checks if player's inventory is full.
		Returns:
			True if the player's inventory is full, False otherwise.
		'''
		return len(player_Data["inventory"]) >= 28

	def get_Inventory(self) -> list:
		'''
		Gets a list of dicts representing the player inventory.
		Returns:
			A list of dicts with the following keys:
				- index: The position of the item in the inventory.
				- id: The item ID.
				- quantity: The quantity of the item.
		Example:
			for item in inv:
				print(f"Slot: {item['index']}, Item ID: {item['id']}, Amount: {item['amount']}")
		'''
		return player_Data["inventory"]
	
	def get_IndexesOfItemsInInventory(self, id: Union[List[int], int]) -> list:
		'''
		For the given item ID, returns a list of inventory slot indexes that the item exists in.
		Useful for locating items you do not want to drop.
		Args:
			id: The item ID to search for (an single ID, or list of IDs).
		Returns:
			A list of inventory slot indexes that the item exists in.
		'''
		inv = player_Data["inventory"]
		if isinstance(id, int):
			return [slot['index'] for slot in inv if slot['id'] == id]
		elif isinstance(id, list):
			return [slot['index'] for slot in inv if slot['id'] in id]

	def get_IsPlayerIdle(self) -> bool:
		'''
		Checks if the player is idle. Note, this does not check if the player is moving - it only
		checks if they are performing an action animation (skilling, combat, etc).
		Returns:
			True if the player is idle, False otherwise.
		'''
		# run a loop for 1 second
		start_time = time.time()
		while time.time() - start_time < 1:
			if player_Data["attack"]["animationId"] != -1:
				return False
		return True

	def get_IsPlayerPraying(self) -> bool:
		'''
		Checks if the player is currently praying. Useful for knowing when you've run out of prayer points.
		Returns:
			True if the player is praying, False otherwise.
		'''
		return bool(player_Data["prayers"])

	def get_PlayerEquipment(self) -> list:
		return player_Data["equipment"] or []

	#pass; returns a list of stats like stab, slash, crush, will return all 0s if nothing is worn
	def get_EquipmentStats(self) -> list:
		'''
		Checks your current equipment stats. Includes aStab, aSlash, aCrush, aMagic, aRange,
		dStab, dSlash, dCrush, dMagic, dRange, str, rStr, mDmg.
		Returns:
			A list of your current equipment stats.
		'''
		return player_Data["equipmentStats"]

	def get_AnimationData(self) -> list:
		return player_Data["attack"]["animationName"],player_Data["attack"]["animationId"],player_Data["attack"]["animationIsSpecial"],player_Data["attack"]["animationBaseSpellDmg"]

	def get_AnimationID(self) -> int:
		return player_Data["attack"]["animationId"] 


# Test Code
if __name__ == "__main__":
	print("Attempting to start server...")
	api = API()

	while True:
		#api.get_PlayerData()
		time.sleep(api.gameTick)
		# print(f"Run Energy: {api.get_PlayerRunEnergy()}")
		# print(f"Is Inventory Full: {api.get_IsInventoryFull()}")
		# print(f"Inventory: {api.get_Inventory()}")
		# print(f"Indexes of bones and chickens in inventory: {api.get_IndexesOfItemsInInventory([526, 2138])}")
		# print(f"Indexs of bones in inventory: {api.get_IndexesOfItemsInInventory(526)}")
		# print(f"Is Player Praying: {api.get_IsPlayerPraying()}")
		# print(f"Players Prayers: {api.get_PlayersPrayers()}")
		# print(f"Player Equipment: {api.get_PlayerEquipment()}")
		# print(f"Equipment Stats: {api.get_EquipmentStats()}")
		# print(f"Is Player Idle: {api.get_IsPlayerIdle()}")
		# print(f"Animation Data: {api.get_AnimationData()}")
		# print(f"Animation Name: {api.get_AnimationName()}")
		# print(f"Animation ID: {api.get_AnimationID()}")

		print("-----------------------------")
