import customtkinter
from controller.bot_controller import BotController
from model.example_bot import ExampleBot
from views.bot_view import BotView


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 650
    HEIGHT = 520

    def __init__(self):
        super().__init__()

        self.title("OSNR Bot")
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
                                              text_font=("Roboto Medium", -16))
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.button_list = []
        self.btn_example_bot = customtkinter.CTkButton(master=self.frame_left,
                                                       text="Example",
                                                       fg_color=("gray75", "gray30"),
                                                       command=lambda: self.show_frame("Example", self.btn_example_bot))
        self.btn_example_bot.grid(row=2, column=0, pady=10, padx=20)
        self.button_list.append(self.btn_example_bot)

        self.btn_example_bot2 = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Example 2",
                                                        fg_color=("gray75", "gray30"),
                                                        command=lambda: self.show_frame("Example 2", self.btn_example_bot2))
        self.btn_example_bot2.grid(row=3, column=0, pady=10, padx=20)
        self.button_list.append(self.btn_example_bot2)

        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text="Dark Mode",
                                              command=self.change_mode)
        self.switch.grid(row=10, column=0, pady=10, padx=20, sticky="w")
        self.switch.select()

        # ============ frame_right ============
        self.view_list = {}
        # Example Bot
        self.view_list["Example"] = BotView(parent=self.frame_right)
        self.example_model = ExampleBot()
        self.example_controller = BotController(model=self.example_model, view=self.view_list["Example"])
        self.view_list["Example"].setup(controller=self.example_controller,
                                        title=self.example_model.title,
                                        description=self.example_model.description)
        # Example Bot 2
        self.view_list["Example 2"] = BotView(parent=self.frame_right)

    # ============ Script button handlers ============
    def hide_all_frames(self):
        # TODO: stop running threads
        # set all buttons to default color
        for button in self.button_list:
            button.config(fg_color=("gray75", "gray30"))
        for view in self.view_list.values():
            view.pack_forget()

    def show_frame(self, name, btn):
        self.hide_all_frames()
        btn.config(fg_color=btn.hover_color)
        self.view_list[name].pack(fill="both", expand=1)

    # ============ Misc handler ============
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
