from model.bot import BotStatus
from model.runelite_bot import RuneLiteBot
from utilities.socket_data import Socket, SocketError
import time


class SocketTest(RuneLiteBot):
	def __init__(self):
		title = "Socket Test"
		description = "Testing Socket Functionality"
		super().__init__(title=title, description=description)
		self.running_time = 1

	def create_options(self):
		self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 180)  # max 180 minutes

	def save_options(self, options: dict):
		self.options_set = True

	def main_loop(self):  # sourcery skip: min-max-identity, switch

		# --- CLIENT SETUP ---
		#self.setup_client()
		socket = Socket()

		# --- RUNTIME PROPERTIES ---

		# --- MAIN LOOP ---

		start_time = time.time()
		end_time = self.running_time * 60
		while time.time() - start_time < end_time:
			# TODO: Ensure fully logged in before Socket can be called
			# TODO: HTTP Plugin installed before socket can be called

			print(f"HP: {socket.get_hitpoints()[0]}")
			print(f"WC Level: {socket.get_stat_level('woodcutting')}")
			print(f"Player Position: {socket.get_player_position()}")
			time.sleep(2)

			# status check
			if not self.status_check_passed():
				print("Bot stopped.")
				return

		# If the bot reaches here it has completed its running time.
		self.update_progress(1)
		self.log_msg("Bot has completed all of its iterations.")
		self.set_status(BotStatus.STOPPED)
