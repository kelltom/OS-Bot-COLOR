import customtkinter
import pathlib
from PIL import Image, ImageTk
import pyperclip as pc


class DefaultView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Title
        self.grid_rowconfigure(2, weight=0)  # - Desc
        self.grid_rowconfigure(3, weight=0)  # - Login
        self.grid_rowconfigure(4, weight=0)  # - Copy text
        self.grid_rowconfigure(5, weight=1)  # Spacing

        # Images
        PATH = pathlib.Path(__file__).parent.parent.resolve()
        img_size = 18
        full_img_width = img_size + 5
        self.img_copy = ImageTk.PhotoImage(Image.open(f"{PATH}/images/ui/copy.png").resize((img_size, img_size)), Image.ANTIALIAS)

        # Title label
        self.label_title = customtkinter.CTkLabel(master=self,
                                                  text="Welcome to OSRS Bot!",
                                                  text_font=("Roboto Medium", 18))
        self.label_title.grid(row=1, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Description label
        self.description = ("Before you begin, please run the OSRS Runelite client and log in with the credentials below. " +
                            "If you are unable to log in, replace your Runelite settings with ./src/runelite_settings/settings.properties manually. " + 
                            "Some scripts rely on specific Runelite plugins and settings.")
        self.label_description = customtkinter.CTkLabel(master=self,
                                                        text=self.description,
                                                        text_font=("Roboto", 14))
        self.label_description.bind('<Configure>', lambda e: self.label_description.config(wraplength=self.label_description.winfo_width()-20))
        self.label_description.grid(row=2, column=0, sticky="nwes", padx=15)

        # Login Frame 2x3
        self.login_frame = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.login_frame.grid(row=3, column=0, sticky="nwes", padx=40, pady=15)
        self.login_frame.grid_columnconfigure(0, weight=0, minsize=full_img_width)  # spacing
        self.login_frame.grid_columnconfigure(1, weight=1)  # email
        self.login_frame.grid_columnconfigure(2, weight=1)  # password
        self.login_frame.grid_columnconfigure(3, weight=0, minsize=full_img_width)  # clipboard buttons

        self.login_frame.grid_rowconfigure(0, weight=0)
        self.login_frame.grid_rowconfigure(1, weight=0)

        # Runelite account credentials
        self.email = "osnrbot@gmail.com"
        self.password = "TBD"

        # Email
        self.lbl_email = customtkinter.CTkLabel(master=self.login_frame,
                                                text=("Login: "),
                                                text_font=("Roboto", 12))
        self.lbl_email.grid(row=0, column=1, sticky="nes")

        self.lbl_email_text = customtkinter.CTkLabel(master=self.login_frame,
                                                     text=self.email,
                                                     text_font=("Roboto", 12))
        self.lbl_email_text.grid(row=0, column=2, sticky="nws")

        self.btn_copy_email = customtkinter.CTkButton(master=self.login_frame,
                                                      text="",
                                                      fg_color="gray40",
                                                      hover_color="gray25",
                                                      width=full_img_width,
                                                      corner_radius=0,
                                                      image=self.img_copy,
                                                      command=self.copy_email_to_clipboard)
        self.btn_copy_email.grid(row=0, column=3, sticky="ns")

        # Password
        self.lbl_password = customtkinter.CTkLabel(master=self.login_frame,
                                                   text="Password: ",
                                                   text_font=("Roboto", 12))
        self.lbl_password.grid(row=1, column=1, sticky="nes")

        self.lbl_password_text = customtkinter.CTkLabel(master=self.login_frame,
                                                        text=self.password,
                                                        text_font=("Roboto", 12))
        self.lbl_password_text.grid(row=1, column=2, sticky="nws")

        self.btn_copy_password = customtkinter.CTkButton(master=self.login_frame,
                                                         text="",
                                                         fg_color="gray40",
                                                         hover_color="gray25",
                                                         width=full_img_width,
                                                         corner_radius=0,
                                                         image=self.img_copy,
                                                         command=self.copy_password_to_clipboard)
        self.btn_copy_password.grid(row=1, column=3, sticky="ns")

        # Copied label
        self.lbl_copy_text = customtkinter.CTkLabel(master=self,
                                                    text="")
        self.lbl_copy_text.grid(row=4, column=0, sticky="nwes")

    def copy_email_to_clipboard(self):
        pc.copy(self.email)
        self.lbl_copy_text.config(text="Email copied to clipboard!")

    def copy_password_to_clipboard(self):
        pc.copy(self.password)
        self.lbl_copy_text.config(text="Password copied to clipboard!")
