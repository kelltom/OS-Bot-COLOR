import customtkinter
from controller.bot_controller import BotController
from model.cerberus import Cerberus
from views.cerberus_view import CerberusView
from views.zulrah_view import ZulrahView


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
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.button_list = []
        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Cerberus",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.show_cerberus_view)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)
        self.button_list.append(self.button_1)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Overloads",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.button_event)
        self.button_2.grid(row=3, column=0, pady=10, padx=20)
        self.button_list.append(self.button_2)

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Zulrah",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.show_zulrah_view)
        self.button_3.grid(row=4, column=0, pady=10, padx=20)
        self.button_list.append(self.button_3)

        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text="Dark Mode",
                                              command=self.change_mode)
        self.switch.grid(row=10, column=0, pady=10, padx=20, sticky="w")
        self.switch.select()

        # ============ frame_right ============
        # Cerberus Script
        self.cerberus_frame = CerberusView(parent=self.frame_right)
        self.cerberus_model = Cerberus()
        self.cerberus_controller = BotController(model=self.cerberus_model, view=self.cerberus_frame)
        self.cerberus_frame.set_controller(self.cerberus_controller)
        # Zulrah Script
        self.zulrah_frame = ZulrahView(parent=self.frame_right)

    # ============ Script button handlers ============
    def hide_all_frames(self):
        # set all buttons to default color
        for button in self.button_list:
            button.config(fg_color=("gray75", "gray30"))
        self.cerberus_frame.pack_forget()
        self.zulrah_frame.pack_forget()

    # TODO: These functions should call controller functions from the views to stop
    # any scripts that are still running before switching to a new one.
    def show_cerberus_view(self):
        self.hide_all_frames()
        # set button color to indicate active script
        self.button_1.config(fg_color=self.button_1.hover_color)
        self.cerberus_frame.pack(fill="both", expand=1)

    def show_zulrah_view(self):
        self.hide_all_frames()
        self.button_3.config(fg_color=self.button_3.hover_color)
        self.zulrah_frame.pack(fill="both", expand=1)

    # ============ Misc handlers ============
    def button_event(self):
        print("Button pressed")

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
