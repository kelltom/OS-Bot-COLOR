from model.bot import BotStatus
from model.runelite_bot import RuneLiteBot
from utilities.API import API, SocketError
import time


class SocketTest(RuneLiteBot):
	def __init__(self):
		title = "Socket Test"
		description = "Testing Socket Functionality"
		super().__init__(title=title, description=description)
		self.running_time = 1
		self.test_type = "player data"

	def create_options(self):
		self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 180)
		self.options_builder.add_checkbox_option("test_type", "Test Type", ["player data", "inv data", "world data", "wait for xp"])

	def save_options(self, options: dict):
		self.options_set = True
		for option in options:
			if option == "running_time":
				self.running_time = options[option]
				self.log_msg(f"Running time set to {self.running_time} minutes.")
			elif option == "test_type":
				self.test_type = options[option]
				self.log_msg(f"Test type set to {self.test_type}.")
			else:
				self.log_msg(f"Unknown option: {option}")
				self.options_set = False
		
		if self.options_set:
			self.log_msg("Options set successfully.")
		else:
			self.log_msg("Failed to set options.")
			print("Developer: ensure option keys are correct.")

	def main_loop(self):  # sourcery skip: min-max-identity, switch

		# --- CLIENT SETUP ---
		#self.setup_client()
		api = API()

		# --- ENDPOINT TEST ---
		if api.test_endpoints():
			print("Endpoints are working!")
		else:
			print("Bot stopped.")
			self.set_status(BotStatus.STOPPED)
			return

		# --- MAIN LOOP ---

		start_time = time.time()
		end_time = self.running_time * 60
		while time.time() - start_time < end_time:

			if "player data" in self.test_type:

				# Example of safely getting player data
				if hp := api.get_hitpoints():
					print(f"Current HP: {hp[0]}")
					print(f"Max HP: {hp[1]}")
				
				print(f"Run Energy: {api.get_run_energy()}")
				print(f"get_animation(): {api.get_animation()}")
				print(f"get_animation_id(): {api.get_animation_id()}")
				print(f"Is player idle: {api.get_is_player_idle()}")
				
			
			if "world data" in self.test_type:
				print(f"Game tick: {api.get_game_tick()}")
				print(f"Player position: {api.get_player_position()}")
				print(f"Player region data: {api.get_player_region_data()}")
				print(f"Mouse position: {api.get_mouse_position()}")
				#print(f"get_interaction_code(): {api.get_interaction_code()}")
				print(f"Is in combat?: {api.get_is_in_combat()}")
				print(f"get_npc_health(): {api.get_npc_hitpoints()}")
			
			if "inv data" in self.test_type:
				print(f"Are logs in inventory?: {api.get_if_item_in_inv(item_id=1511)}")
				print(f"Find logs in inv: {api.find_item_in_inv(item_id=1511)}")
			
			if "wait for xp" in self.test_type:
				print(f"WC Level: {api.get_skill_level('woodcutting')}")
				print(f"WC XP: {api.get_skill_xp('woodcutting')}")
				print(f"WC XP Gained: {api.get_skill_xp_gained('woodcutting')}")
				print("---waiting for wc xp to be gained---")
				if api.wait_til_gained_xp(skill="woodcutting", timeout=10):
					print("Gained xp!")
				else:
					print("No xp gained.")

			time.sleep(2)

			print("\n--------------------------\n")

			# status check
			if not self.status_check_passed():
				print("Bot stopped.")
				return

		# If the bot reaches here it has completed its running time.
		self.update_progress(1)
		self.log_msg("Bot has completed all of its iterations.")
		self.set_status(BotStatus.STOPPED)
