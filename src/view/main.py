import tkinter
import tkinter.messagebox
import customtkinter
from script_views.cerberus_view import CerberusView
from script_views.zulrah_view import ZulrahView


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()

        self.title("OSNR Bot")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")

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

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Cerberus",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.show_cerberus_view)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Overloads",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.button_event)
        self.button_2.grid(row=3, column=0, pady=10, padx=20)

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Zulrah",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.show_zulrah_view)
        self.button_3.grid(row=4, column=0, pady=10, padx=20)

        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text="Dark Mode",
                                              command=self.change_mode)
        self.switch.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============
        # TODO: create a variable that instantiates an instance of a custom Frame class (e.g.,
        # cerberus_frame = CerberusFrame(parent=self.frame_right)
        # zulrah_frame = ZulrahFrame(parent=self.frame_right)
        # THEN, create a function that will be a button handler for a Script button that will hide other frames
        # before placing the new one at the top. E.g.,
        # show_cerberus_view():
        #   hide_all_frames() (involves {frame variable}.pack_forget() )
        #   cerberus_frame.pack(fill="both", expand=1)
        #
        # These should be functions of a root controller. Each view should have its own controller for
        # manipulating scripts, and everything should be terminated upon switching scripts.

        self.cerberus_frame = CerberusView(parent=self.frame_right)
        self.zulrah_frame = ZulrahView(parent=self.frame_right)

        # TODO: The following should be configurations within custom Frame classes
        # parent.rowconfigure(0, weight=0)  # Contains the view for settings/control
        # parent.rowconfigure(1, weight=1)  # Contains the view for progress log (resizable)

    def hide_all_frames(self):
        self.cerberus_frame.pack_forget()
        self.zulrah_frame.pack_forget()

    def show_cerberus_view(self):
        self.hide_all_frames()
        self.cerberus_frame.pack(fill="both", expand=1)

    def show_zulrah_view(self):
        self.hide_all_frames()
        self.zulrah_frame.pack(fill="both", expand=1)

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
