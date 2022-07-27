import customtkinter
from controller.bot_controller import BotController
from model.alora_combat import AloraCombat
from model.example_bot import ExampleBot
import tkinter
from view.bot_view import BotView
from view.home_view import HomeView
from view.option_views.example_bot_options import ExampleBotOptions


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 650
    HEIGHT = 520

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

        # script buttons
        self.btn_list = []
        self.btn_example_bot = customtkinter.CTkButton(master=self.frame_left,
                                                       text="Example",
                                                       command=lambda: self.toggle_frame_by_name("Example", self.btn_example_bot))
        self.btn_example_bot.grid(row=2, column=0, pady=10, padx=20)
        self.btn_list.append(self.btn_example_bot)

        self.btn_example_bot2 = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Example 2",
                                                        command=lambda: self.toggle_frame_by_name("Example 2", self.btn_example_bot2))
        self.btn_example_bot2.grid(row=3, column=0, pady=10, padx=20)
        self.btn_list.append(self.btn_example_bot2)

        self.btn_alora_combat = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Alora Combat",
                                                        command=lambda: self.toggle_frame_by_name("AloraCombat", self.btn_alora_combat))
        self.btn_alora_combat.grid(row=4, column=0, pady=10, padx=20)
        self.btn_list.append(self.btn_alora_combat)

        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text="Dark Mode",
                                              command=self.change_mode)
        self.switch.grid(row=10, column=0, pady=10, padx=20, sticky="w")
        self.switch.select()

        self.__configure_all_buttons()

        # ============ frame_right ============
        self.home_view = HomeView(parent=self.frame_right, main=self)
        self.home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)

        # Create Bot Views here
        self.views = {}

        # Example Bot
        self.views["Example"] = BotView(parent=self.frame_right)
        self.example_model = ExampleBot()
        self.example_controller = BotController(model=self.example_model, view=self.views["Example"])
        self.views["Example"].setup(controller=self.example_controller,
                                    title=self.example_model.title,
                                    description=self.example_model.description,
                                    options_class=ExampleBotOptions)
        # Example Bot 2
        self.views["Example 2"] = BotView(parent=self.frame_right)

        # Alora Combat bot
        self.views["AloraCombat"] = BotView(parent=self.frame_right)
        self.alora_combat_model = AloraCombat()
        self.alora_combat_controller = BotController(model=self.alora_combat_model, view=self.views["AloraCombat"])
        self.views["AloraCombat"].setup(controller=self.alora_combat_controller,
                                        title=self.alora_combat_model.title,
                                        description=self.alora_combat_model.description,
                                        options_class=ExampleBotOptions)

        self.current_view = None
        self.current_btn = None

        self.__configure_all_buttons()

    # ============ Script button handlers ============
    def toggle_frame_by_name(self, name, btn):
        if self.views[name] is not None:
            # If the script's frame is already visible, hide it
            if self.current_view is self.views[name]:
                self.current_view.pack_forget()
                self.current_view = None
                self.current_btn.configure(fg_color=("gray75", "gray30"))
                self.current_btn = None
                self.home_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
            # If a different script is selected, hide it and show the new one
            elif self.current_view is not None:
                self.current_view.pack_forget()
                self.current_view = self.views[name]
                self.current_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
                self.current_btn.configure(fg_color=("gray75", "gray30"))
                self.current_btn = btn
                self.current_btn.configure(fg_color=btn.hover_color)
            # If no script is selected, show the new one
            else:
                self.home_view.pack_forget()
                self.current_view = self.views[name]
                self.current_view.pack(in_=self.frame_right, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
                self.current_btn = btn
                self.current_btn.configure(fg_color=btn.hover_color)

    # ============ Misc handler ============
    def enable_all_buttons(self):
        for btn in self.btn_list:
            btn.configure(state="normal")

    def __configure_all_buttons(self):
        for btn in self.btn_list:
            btn.configure(state="disabled", fg_color=("gray75", "gray30"))

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
