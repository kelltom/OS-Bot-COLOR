from OSBC import App
from controller.bot_controller import BotController, MockBotController
from model import Bot, RuneLiteBot
from pynput import keyboard

import time
import random

def launchRun(bot: Bot):
    bot.set_controller(MockBotController(bot))
    bot.options_set = True
    App.listener = keyboard.Listener(
        on_press=lambda event: App.__on_press(event, bot),
        on_release=None,
    )
    bot.launch_game()
    App.listener.start()
    bot.play()
    App.listener.join()

if __name__ == "__main__":
    # To test a bot without the GUI, address the comments for each line below.
    # from model.<folder_bot_is_in> import <bot_class_name>  # Uncomment this line and replace <folder_bot_is_in> and <bot_class_name> accordingly to import your bot
    # app = App()  # Add the "test=True" argument to the App constructor call.
    # app.start()  # Comment out this line.
    # app.test(Bot())  # Uncomment this line and replace argument with your bot's instance.

    # IMPORTANT
    # - Make sure your bot's options are pre-defined in its __init__ method.
    # - You can stop the bot by pressing `Left Ctrl`
    from model.osrs.combat.combat import OSRSCombat
    app = App(test=True)
    app.launchRun(OSRSCombat())