import customtkinter
from controller.bot_controller import BotController
from model.alora_combat import AloraCombat
from model.example_bot import ExampleBot
import tkinter
from view.bot_view import BotView
from view.home_view import HomeView
from view.osnr_home_view import OSNRHomeView
from view.rl_home_view import RuneliteHomeView


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 650
    HEIGHT = 520
    DEFAULT_GRAY = ("gray75", "gray30")

    def __init__(self):  # sourcery skip: merge-list-append, move-assign-in-block
        super().__init__()

        self.title("OSRS Bot COLOR")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,  # static width on left-hand sidebar = non-resizable
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_left ============

        # configure grid layout (11x1)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing (top padding above title)
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing (resizable spacing between buttons and switches)
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing (adds a top padding to switch section)
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing (bottom padding below switches)

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Scripts",
                                              text_font=("Roboto Medium", 14))
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        # Button map (key: game title, value: list of buttons)
        self.btn_map = {
            "Select a game": [],
            "OSRS": [],
            "Alora": [],
            "OSNR": []
        }

        self.menu_game_selector = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                              values=list(self.btn_map.keys()),
                                                              command=self.__on_game_selector_change)
        self.menu_game_selector.grid(row=2, column=0, sticky="we", padx=10, pady=10)

        # Script Buttons (be sure to append the buttons to their respective game in the button map)
        # OSRS
        self.btn_example_bot = customtkinter.CTkButton(master=self.frame_left,
                                                       text="Example",
                                                       fg_color=self.DEFAULT_GRAY,
                                                       command=lambda: self.__toggle_bot_by_name("ExampleBot", self.btn_example_bot))
        self.btn_map["OSRS"].append(self.btn_example_bot)

        self.btn_example_bot2 = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Example 2",
                                                        fg_color=self.DEFAULT_GRAY,
                                                        command=lambda: self.__toggle_bot_by_name("ExampleBot2", self.btn_example_bot2))
        self.btn_map["OSRS"].append(self.btn_example_bot2)

        # Alora
        self.btn_alora_combat = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Combat",
                                                        fg_color=self.DEFAULT_GRAY,
                                                        command=lambda: self.__toggle_bot_by_name("AloraCombat", self.btn_alora_combat))
        self.btn_map["Alora"].append(self.btn_alora_combat)

        # Theme Switch
        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text="Dark Mode",
                                              command=self.change_mode)
        self.switch.grid(row=10, column=0, pady=10, padx=20, sticky="w")
        self.switch.select()

        # ============ frame_right ============
        self.views = {}
        self.models = {}

        # Home Views ('Select a game' has the default HomeView)
        # Non-runelite games will have custom home views
        self.runelite_home_view = RuneliteHomeView(parent=self.frame_right, main=self)
        self.home_view = HomeView(parent=self.frame_right, main=self)
        self.home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        self.views["Select a game"] = self.home_view
        self.views["OSRS"] = self.runelite_home_view
        self.views["Alora"] = self.runelite_home_view
        self.views["OSNR"] = OSNRHomeView(parent=self, main=self)

        # Declare script view and controller
        self.views["Script"] = BotView(parent=self.frame_right)
        self.controller = BotController(model=None, view=self.views["Script"])
        self.views["Script"].set_controller(self.controller)

        # OSRS Bots (examples)
        self.models["ExampleBot"] = ExampleBot()
        self.models["ExampleBot"].set_controller(self.controller)
        self.models["ExampleBot2"] = ExampleBot()
        self.models["ExampleBot2"].set_controller(self.controller)

        # Alora Bots
        self.models["AloraCombat"] = AloraCombat()
        self.models["AloraCombat"].set_controller(self.controller)

        # Status variables to track state of views and buttons
        self.current_home_view = self.views["Select a game"]
        self.current_script_view = None
        self.current_btn = None
        self.current_btn_list = None

    # ============ Script button handlers ============
    def __on_game_selector_change(self, choice):
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
        self.controller.update_model(None)
        # Pack new buttons
        self.current_btn_list = self.btn_map[choice]
        for r, btn in enumerate(self.current_btn_list, 3):
            btn.grid(row=r, column=0, sticky="we", padx=10, pady=10)
        # Repack new home view
        self.current_home_view.pack_forget()
        self.current_home_view = self.views[choice]
        if isinstance(self.current_home_view, RuneliteHomeView):
            self.current_home_view.update(title=choice)
        self.current_home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        self.toggle_btn_state(enabled=False)

    def __toggle_bot_by_name(self, name, btn):
        if self.models[name] is not None:
            # If the script's frame is already visible, hide it
            if self.controller.model == self.models[name]:
                self.controller.update_model(None)
                self.views["Script"].pack_forget()
                self.current_script_view = None
                self.current_btn.configure(fg_color=self.DEFAULT_GRAY)
                self.current_btn = None
                self.current_home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
            # If there is no script selected
            elif self.controller.model is None:
                self.current_home_view.pack_forget()
                self.controller.update_model(self.models[name])
                self.views["Script"].pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
                self.current_btn = btn
                self.current_btn.configure(fg_color=btn.hover_color)
            # If we are switching to a new script
            else:
                self.controller.update_model(self.models[name])
                self.current_btn.configure(fg_color=self.DEFAULT_GRAY)
                self.current_btn = btn
                self.current_btn.configure(fg_color=btn.hover_color)

    # ============ Misc handler ============
    def toggle_btn_state(self, enabled: bool):
        if self.current_btn_list is not None:
            for btn in self.current_btn_list:
                if enabled:
                    btn.configure(state="normal")
                else:
                    btn.configure(state="disabled")

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
