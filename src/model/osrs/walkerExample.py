import utilities.api.locations as loc
from model.osrs.osrs_bot import OSRSBot
from utilities.walker import Walking


class OSRSWalkingExample(OSRSBot):

    def __init__(self):
        self.walk_to = "VARROCK_SQUARE"
        super().__init__(bot_title="Walk", description="Walk almost anywhere")

    def create_options(self):
        locations = [name for name in vars(loc) if not name.startswith("__")]
        self.options_builder.add_dropdown_option("walk_to", "Walk to?", locations)

    def save_options(self, options: dict):
        for option in options:
            if option == "walk_to":
                self.log_msg(f"walk_to: {options[option]}")
                self.walk_to = options[option]
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        while True:
            walker = Walking(self)
            if walker.walk_to(self.walk_to):
                self.log_msg("Arrived at destination")
                self.stop()
            self.stop()
