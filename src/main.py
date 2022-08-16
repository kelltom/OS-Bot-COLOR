import customtkinter
from controller.bot_controller import BotController
from model.alora.combat import AloraCombat
from model.osnr.runecraft_astral import OSNRAstralRunes
from model.osnr.combat import OSNRCombat
from model.osnr.fishing import OSNRFishing
from model.osnr.mining import OSNRMining
from model.osnr.snape_grass import OSNRSnapeGrass
from model.osnr.thieving_stall import OSNRThievingStall
from model.osnr.thieving_npc import OSNRThievingNPC
from model.osrs.example_bot import ExampleBot
import tkinter
from view.bot_view import BotView
from view.home_view import HomeView
from view.home_view_alora import AloraHomeView
from view.home_view_osnr import OSNRHomeView
from view.home_view_osrs import OSRSHomeView


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 650
    HEIGHT = 520
    DEFAULT_GRAY = ("gray50", "gray30")

    def __init__(self):  # sourcery skip: merge-list-append, move-assign-in-block
        super().__init__()

        self.title("OSRS Bot COLOR")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ Create Two Frames ============

        # configure grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,  # static width on left-hand sidebar = non-resizable
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ Left-Side Menu (frame_left) ============

        # configure grid layout
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing (top padding above title)
        self.frame_left.grid_rowconfigure(18, weight=1)  # empty row as spacing (resizable spacing between buttons and theme switch)
        self.frame_left.grid_rowconfigure(19, minsize=20)    # empty row with minsize as spacing (adds a top padding to theme switch)
        self.frame_left.grid_rowconfigure(21, minsize=10)  # empty row with minsize as spacing (bottom padding below theme switch)

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Scripts",
                                              text_font=("Roboto Medium", 14))
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        # Button map
        # There should be a key for each game title, and the value should be a list of buttons for that game
        self.btn_map = {
            "Select a game": [],
            "Alora": [],
            "Near-Reality": [],  # AKA: OSNR
            "OSRS": []
        }

        # Dropdown menu for selecting a game
        self.menu_game_selector = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                              values=list(self.btn_map.keys()),
                                                              command=self.__on_game_selector_change)
        self.menu_game_selector.grid(row=2, column=0, sticky="we", padx=10, pady=10)

        # Theme Switch
        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text="Dark Mode",
                                              command=self.change_mode)
        self.switch.grid(row=20, column=0, pady=10, padx=20, sticky="w")
        self.switch.select()

        # ============ View/Controller Configuration ============
        self.views = {}  # A map of all views, keyed by game title
        self.models = {}  # A map of all models, keyed by bot title

        # Home Views
        self.home_view = HomeView(parent=self.frame_right, main=self)
        self.home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        self.views["Select a game"] = self.home_view
        self.views["OSRS"] = OSRSHomeView(parent=self, main=self)
        self.views["Alora"] = AloraHomeView(parent=self, main=self)
        self.views["Near-Reality"] = OSNRHomeView(parent=self, main=self)

        # Script view and controller [DO NOT EDIT]
        # self.views["Script"] is a dynamically changing view on frame_right that changes based on the model assigned to the controller
        self.views["Script"] = BotView(parent=self.frame_right)
        self.controller = BotController(model=None, view=self.views["Script"])
        self.views["Script"].set_controller(self.controller)

        # ============ Bot/Button Configuration ============

        # TEMPLATE FOR ADDING BOTS
        # 1. Create an instance of your Bot and append it to the bot map (self.models) with a unique, descriptive key.
        # 2. Set the controller of the bot to self.controller.
        # 3. Call the "__create_button" function to create a pre-configured button for the bot. Append the button to
        #    the button map (self.btn_map) for the game it belongs to.

        # ----- Old School Runescape (OSRS) Bots -----
        self.models["ExampleBot"] = ExampleBot()
        self.models["ExampleBot"].set_controller(self.controller)
        self.btn_map["OSRS"].append(self.__create_button("ExampleBot"))

        self.models["ExampleBot2"] = ExampleBot()
        self.models["ExampleBot2"].set_controller(self.controller)
        self.btn_map["OSRS"].append(self.__create_button("ExampleBot"))

        # ----- Old School Near-Reality (OSNR) Bots -----
        self.models["OSNRCombat"] = OSNRCombat()
        self.models["OSNRCombat"].set_controller(self.controller)
        self.btn_map["Near-Reality"].append(self.__create_button("OSNRCombat"))

        self.models["OSNRFishing"] = OSNRFishing()
        self.models["OSNRFishing"].set_controller(self.controller)
        self.btn_map["Near-Reality"].append(self.__create_button("OSNRFishing"))

        self.models["OSNRMining"] = OSNRMining()
        self.models["OSNRMining"].set_controller(self.controller)
        self.btn_map["Near-Reality"].append(self.__create_button("OSNRMining"))

        self.models["OSNRAstral"] = OSNRAstralRunes()
        self.models["OSNRAstral"].set_controller(self.controller)
        self.btn_map["Near-Reality"].append(self.__create_button("OSNRAstral"))

        self.models["OSNRSnapegrass"] = OSNRSnapeGrass()
        self.models["OSNRSnapegrass"].set_controller(self.controller)
        self.btn_map["Near-Reality"].append(self.__create_button("OSNRSnapegrass"))

        self.models["OSNRThievingNPC"] = OSNRThievingNPC()
        self.models["OSNRThievingNPC"].set_controller(self.controller)
        self.btn_map["Near-Reality"].append(self.__create_button("OSNRThievingNPC"))

        self.models["OSNRThievingStall"] = OSNRThievingStall()
        self.models["OSNRThievingStall"].set_controller(self.controller)
        self.btn_map["Near-Reality"].append(self.__create_button("OSNRThievingStall"))

        # ----- Alora Bots -----
        self.models["AloraCombat"] = AloraCombat()
        self.models["AloraCombat"].set_controller(self.controller)
        self.btn_map["Alora"].append(self.__create_button("AloraCombat"))

        # Status variables to track state of views and buttons
        self.current_home_view = self.views["Select a game"]
        self.current_btn = None
        self.current_btn_list = None

    # ============ UI Creation Helpers ============
    def __create_button(self, bot_key):
        '''
        Creates a preconfigured button for the bot.
        Args:
            bot_key: str - the key of the bot as it exists in it's dictionary.
        Returns:
            Tkinter.Button - the button created.
        '''
        btn = customtkinter.CTkButton(master=self.frame_left,
                                      text=self.models[bot_key].title,
                                      fg_color=self.DEFAULT_GRAY,
                                      command=lambda: self.__toggle_bot_by_key(bot_key, btn))
        return btn

    def toggle_btn_state(self, enabled: bool):
        '''
        Toggles the state of the buttons in the current button list.
        Args:
            enabled: bool - True to enable buttons, False to disable buttons.
        '''
        if self.current_btn_list is not None:
            for btn in self.current_btn_list:
                if enabled:
                    btn.configure(state="normal")
                else:
                    btn.configure(state="disabled")

    # ============ Button Handlers ============
    def __on_game_selector_change(self, choice):
        '''
        Handles the event that occurs when the user selects a game title from the dropdown menu.
        Args:
            choice: The key of the game that the user selected.
        '''
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
        self.current_home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        self.toggle_btn_state(enabled=False)

    def __toggle_bot_by_key(self, bot_key, btn):
        '''
        Handles the event of the user selecting a bot from the dropdown menu. This function manages the state of frame_left buttons,
        the contents that appears in frame_right, and re-assigns the model to the controller.
        Args:
            bot_key: The name/key of the bot that the user selected.
            btn: The button that the user clicked.
        '''
        if self.models[bot_key] is not None:
            # If the script's frame is already visible, hide it
            if self.controller.model == self.models[bot_key]:
                self.controller.change_model(None)
                self.views["Script"].pack_forget()
                self.current_btn.configure(fg_color=self.DEFAULT_GRAY)
                self.current_btn = None
                self.current_home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
            # If there is no script selected
            elif self.controller.model is None:
                self.current_home_view.pack_forget()
                self.controller.change_model(self.models[bot_key])
                self.views["Script"].pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
                self.current_btn = btn
                self.current_btn.configure(fg_color=btn.hover_color)
            # If we are switching to a new script
            else:
                self.controller.change_model(self.models[bot_key])
                self.current_btn.configure(fg_color=self.DEFAULT_GRAY)
                self.current_btn = btn
                self.current_btn.configure(fg_color=btn.hover_color)

    # ============ Misc Handlers ============
    def change_mode(self):
        if self.switch.get() == 1:
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
