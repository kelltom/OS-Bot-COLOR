import importlib
import pathlib
import tkinter
from typing import List

import customtkinter
from PIL import Image, ImageTk
from pynput import keyboard
from tktooltip import ToolTip

import utilities.settings as settings
from controller.bot_controller import BotController, MockBotController
from model import Bot, RuneLiteBot
from utilities.game_launcher import Launchable
from view import *
from view.fonts.fonts import *

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    WIDTH = 680
    HEIGHT = 480
    DEFAULT_GRAY = ("gray50", "gray30")

    def __init__(self, test: bool = False):
        super().__init__()
        self.__init_settings()
        if not test:
            ui_images_path = pathlib.Path(__file__).parent.resolve().joinpath("images", "ui")
            self.img_rocket = ImageTk.PhotoImage(
                Image.open(ui_images_path.joinpath("rocket.png")).resize((12, 12)),
                Image.Resampling.LANCZOS,
            )
            self.img_settings = ImageTk.PhotoImage(
                Image.open(ui_images_path.joinpath("options.png")).resize((12, 12)),
                Image.Resampling.LANCZOS,
            )
            self.build_ui()

    def build_ui(self):  # sourcery skip: merge-list-append, move-assign-in-block
        self.title("OS Bot COLOR")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ Create Two Frames ============

        # configure grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(
            master=self,
            corner_radius=0,
        )
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ View/Controller Configuration (frame_right) ============
        self.views: dict[str, customtkinter.CTkFrame] = {}  # A map of all views, keyed by game title
        self.models: dict[str, Bot] = {}  # A map of all models (bots), keyed by bot title

        # Home Views
        self.home_view = TitleView(parent=self.frame_right, main=self)
        self.home_view.pack(
            in_=self.frame_right,
            side=tkinter.TOP,
            fill=tkinter.BOTH,
            expand=True,
            padx=0,
            pady=0,
        )
        self.views["Select a game"] = self.home_view

        # Script view and controller [DO NOT EDIT]
        # self.views["Script"] is a dynamically changing view on frame_right that changes based on the model assigned to the controller
        self.views["Script"] = BotView(parent=self.frame_right)
        self.controller = BotController(model=None, view=self.views["Script"])
        self.views["Script"].set_controller(self.controller)

        # ============ Left-Side Menu (frame_left) ============

        # Configure grid layout
        self.frame_left.grid_columnconfigure(0, weight=0)  # label
        self.frame_left.grid_columnconfigure(1, weight=0)  # dropdown
        self.frame_left.grid_rowconfigure(2, weight=1)  # buttons
        self.frame_left.grid_rowconfigure(3, weight=0)  # settings

        # Label and dropdown menu inside the scrollable frame
        self.label_1 = customtkinter.CTkLabel(master=self.frame_left, text="Scripts", font=heading_font())
        self.label_1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create Scrollable Frame
        self.scrollable_frame_left = customtkinter.CTkScrollableFrame(master=self.frame_left, width=160, fg_color="#2b2b2b", scrollbar_button_color="#333333")
        self.scrollable_frame_left.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # ============ Bot/Button Configuration (scrollable_frame_left) ============
        # Dynamically import all bots from the model folder and add them to the UI
        # If your bot is not appearing, make sure it is referenced in the __init__.py file of the folder it exists in.

        # Button map
        # Key value pairs of game titles and a list of buttons for that game.
        # This is populated below.
        self.btn_map: dict[str, List[customtkinter.CTkButton]] = {
            "Select a game": [],
        }

        # Dropdown menu for selecting a game
        self.menu_game_selector = customtkinter.CTkOptionMenu(
            master=self.frame_left,
            font=body_large_font(),
            dropdown_font=body_med_font(),
            values=list(self.btn_map.keys()),
            command=self.__on_game_selector_change,
        )
        self.menu_game_selector.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        module = importlib.import_module("model")
        names = dir(module)
        for name in names:
            obj = getattr(module, name)
            if obj is not Bot and obj is not RuneLiteBot and isinstance(obj, type) and issubclass(obj, Bot):
                instance = obj()
                # Make a home view if one doesn't exist
                if isinstance(instance, RuneLiteBot) and instance.game_title not in self.views:
                    self.views[instance.game_title] = RuneLiteHomeView(parent=self, main=self, game_title=instance.game_title)
                elif isinstance(instance, Bot) and instance.game_title not in self.views:
                    self.views[instance.game_title] = HomeView(parent=self, main=self, game_title=instance.game_title)
                # Make a button section if one doesn't exist
                if instance.game_title not in self.btn_map:
                    self.btn_map[instance.game_title] = []
                instance.set_controller(self.controller)
                self.models[name] = instance
                self.btn_map[instance.game_title].append(self.__create_button(bot_key=name, launchable=isinstance(instance, Launchable)))

        # Configure the dropdown values to be list(self.btn_map.keys())
        self.menu_game_selector.configure(values=list(self.btn_map.keys()))

        # Settings Button (in the position of the Theme Switch)
        self.btn_settings = customtkinter.CTkButton(
            master=self.frame_left,
            fg_color="#2a2d2e",
            hover_color=self.DEFAULT_GRAY,
            text="Settings",
            font=button_med_font(),
            image=self.img_settings,
            command=self.__on_settings_clicked,
        )
        self.btn_settings.grid(row=3, column=0, pady=(5, 10), padx=5)

        # Status variables to track state of views and buttons
        self.current_home_view: customtkinter.CTkFrame = self.views["Select a game"]
        self.current_btn: customtkinter.CTkButton = None
        self.current_btn_list: List[customtkinter.CTkButton] = None

    # ============ UI Creation Helpers ============
    def __create_button(self, bot_key: str, launchable: bool = False):
        """
        Creates a preconfigured button for the bot.
        Args:
            bot_key: the key of the bot as it exists in it's dictionary.
            launchable: True if the button should have a little rocket icon.
        Returns:
            Tkinter.Button - the button created.
        """
        max_length = 14 if launchable else 18
        shrink_length = 10 if launchable else 14

        text: str = self.models[bot_key].bot_title
        if len(text) > max_length:
            text = f"{text[:max_length]}..."
            tooltip = True
        else:
            tooltip = False
        font = button_small_font() if len(self.models[bot_key].bot_title) > shrink_length else button_med_font()

        btn = customtkinter.CTkButton(
            master=self.scrollable_frame_left,
            text=text,
            fg_color=self.DEFAULT_GRAY,
            font=font,
            image=self.img_rocket if launchable else None,
            command=lambda: self.__toggle_bot_by_key(bot_key, btn),
        )

        if tooltip:
            ToolTip(btn, delay=0.1, font=small_font(), msg=self.models[bot_key].bot_title, bg="#333333", fg="#ffffff")

        return btn

    def toggle_btn_state(self, enabled: bool):
        """
        Toggles the state of the buttons in the current button list.
        Args:
            enabled: bool - True to enable buttons, False to disable buttons.
        """
        if self.current_btn_list is not None:
            for btn in self.current_btn_list:
                if enabled:
                    btn.configure(state="normal")
                else:
                    btn.configure(state="disabled")

    # ============ Settings Init ============
    def __init_settings(self):
        """
        Initializes the settings for the application.
        """
        # If "keybind" doesn't exist, add default
        keybind = settings.get("keybind")
        if keybind is None:
            settings.set("keybind", settings.default_keybind)

    # ============ Button Handlers ============
    def __on_settings_clicked(self):
        window = customtkinter.CTkToplevel(master=self)
        window.geometry("540x287")
        window.title("Settings")
        view = SettingsView(parent=window)
        view.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        window.after(100, window.lift)  # Workaround for bug where main window takes focus

    def __on_game_selector_change(self, choice):
        """
        Handles the event that occurs when the user selects a game title from the dropdown menu.
        Args:
            choice: The key of the game that the user selected.
        """
        if choice not in list(self.btn_map.keys()):
            return
        # Un-highlight current button
        if self.current_btn is not None:
            self.current_btn.configure(fg_color=self.DEFAULT_GRAY)
            self.current_btn = None
        # Unpack current buttons
        if self.current_btn_list is not None:
            for btn in self.current_btn_list:
                btn.grid_forget()
        # Unpack current script view
        if self.views["Script"].winfo_exists():
            self.views["Script"].pack_forget()
        # Unlink model from controller
        self.controller.change_model(None)
        # Pack new buttons
        self.current_btn_list = self.btn_map[choice]
        for r, btn in enumerate(self.current_btn_list, 3):
            btn.grid(row=r, column=0, sticky="we", padx=10, pady=10)
        # Repack new home view
        self.current_home_view.pack_forget()
        self.current_home_view = self.views[choice]
        self.current_home_view.pack(
            in_=self.frame_right,
            side=tkinter.TOP,
            fill=tkinter.BOTH,
            expand=True,
            padx=0,
            pady=0,
        )
        self.toggle_btn_state(enabled=False)

    def __toggle_bot_by_key(self, bot_key, btn: customtkinter.CTkButton):
        # sourcery skip: extract-method
        """
        Handles the event of the user selecting a bot from the dropdown menu. This function manages the state of frame_left buttons,
        the contents that appears in frame_right, and re-assigns the model to the controller.
        Args:
            bot_key: The name/key of the bot that the user selected.
            btn: The button that the user clicked.
        """
        if self.models[bot_key] is None:
            return
        # If the script's frame is already visible, hide it
        if self.controller.model == self.models[bot_key]:
            self.controller.model.progress = 0
            self.controller.update_progress()
            self.controller.change_model(None)
            self.views["Script"].pack_forget()
            self.current_btn.configure(fg_color=self.DEFAULT_GRAY)
            self.current_btn = None
            self.current_home_view.pack(
                in_=self.frame_right,
                side=tkinter.TOP,
                fill=tkinter.BOTH,
                expand=True,
                padx=0,
                pady=0,
            )
        # If there is no script selected
        elif self.controller.model is None:
            self.current_home_view.pack_forget()
            self.controller.change_model(self.models[bot_key])
            self.views["Script"].pack(
                in_=self.frame_right,
                side=tkinter.TOP,
                fill=tkinter.BOTH,
                expand=True,
                padx=0,
                pady=0,
            )
            self.current_btn = btn
            self.current_btn.configure(fg_color=btn._hover_color)
        # If we are switching to a new script
        else:
            self.controller.model.progress = 0
            self.controller.update_progress()
            self.controller.change_model(self.models[bot_key])
            self.current_btn.configure(fg_color=self.DEFAULT_GRAY)
            self.current_btn = btn
            self.current_btn.configure(fg_color=btn._hover_color)

    # ============ Misc Handlers ============
    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

    # ============ UI-less Test Functions ============
    def test(self, bot: Bot):
        bot.set_controller(MockBotController(bot))
        bot.options_set = True
        self.listener = keyboard.Listener(
            on_press=lambda event: self.__on_press(event, bot),
            on_release=None,
        )
        self.listener.start()
        bot.play()
        self.listener.join()

    def __on_press(self, key, bot: Bot):
        if key == keyboard.Key.ctrl_l:
            bot.thread.stop()
            self.listener.stop()


if __name__ == "__main__":
    # To test a bot without the GUI, address the comments for each line below.
    # from model.<folder_bot_is_in> import <bot_class_name>  # Uncomment this line and replace <folder_bot_is_in> and <bot_class_name> accordingly to import your bot
    app = App()  # Add the "test=True" argument to the App constructor call.
    app.start()  # Comment out this line.
    # app.test(Bot())  # Uncomment this line and replace argument with your bot's instance.

    # IMPORTANT
    # - Make sure your bot's options are pre-defined in its __init__ method.
    # - You can stop the bot by pressing `Left Ctrl`
