"""
Not much effort is going into this Settings UI, as in the future, we'll likely transition to a
different UI framework.
"""


import contextlib
import pathlib

import customtkinter
import pynput.keyboard as keyboard
from PIL import Image, ImageTk

import utilities.settings as settings
from view.fonts.fonts import *


class SettingsView(customtkinter.CTkFrame):
    def __init__(self, parent):
        # sourcery skip: merge-list-append, move-assign-in-block
        super().__init__(parent)
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.current_keys = settings.get("keybind")
        self.combination_keys = []

        # Images
        PATH = pathlib.Path(__file__).parent.parent.joinpath("images", "ui")
        img_size = 18
        self.img_edit = ImageTk.PhotoImage(
            Image.open(f"{PATH}/edit.png").resize((img_size, img_size)),
            Image.ANTIALIAS,
        )
        self.img_check = ImageTk.PhotoImage(
            Image.open(f"{PATH}/check.png").resize((img_size, img_size)),
            Image.ANTIALIAS,
        )

        # As each frame is created, it is added to this list
        widget_list = []

        # === Create widgets ===

        # Keybind Changer
        self.frame_keybinds = customtkinter.CTkFrame(master=self)
        self.frame_keybinds.columnconfigure(0, weight=1)  # lbl label
        self.frame_keybinds.columnconfigure(1, weight=0)  # lbl keybind
        self.frame_keybinds.columnconfigure(2, weight=0)  # btn set
        self.lbl_keybinds = customtkinter.CTkLabel(master=self.frame_keybinds, text="Bot start/stop keybind: ", font=body_med_font())
        self.lbl_keybinds.grid(row=0, column=0, padx=20, pady=20)
        self.entry_keybinds = customtkinter.CTkLabel(
            master=self.frame_keybinds, text=f"{settings.keybind_to_text(self.current_keys) if self.current_keys else 'None'}"
        )
        self.entry_keybinds.grid(row=0, column=1, padx=20, pady=20)
        self.btn_keybinds = customtkinter.CTkButton(
            master=self.frame_keybinds, image=self.img_edit, text="", width=img_size + 10, command=self.__modify_keybind
        )
        self.btn_keybinds.grid(row=0, column=2, padx=20, pady=20)
        widget_list.append(self.frame_keybinds)

        # Keybind Note
        self.note = (
            "Use the `EDIT` button to unlock keyboard input. Press `ESC` to clear input. The new keybind will not be saved until you click the Save button &"
            " restart OSBC."
        )
        self.lbl_keybind_note = customtkinter.CTkLabel(master=self, text=self.note, font=small_font())
        self.lbl_keybind_note.bind(
            "<Configure>",
            lambda e: self.lbl_keybind_note.configure(wraplength=self.lbl_keybind_note.winfo_width() - 10),
        )
        widget_list.append(self.lbl_keybind_note)

        # Grid layout
        self.num_of_widgets = len(widget_list)
        for i in range(self.num_of_widgets):
            self.rowconfigure(i, weight=0)
        self.rowconfigure(self.num_of_widgets + 1, weight=1)  # Spacing between Save btn and options
        self.rowconfigure(self.num_of_widgets + 2, weight=0)  # Save btn
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Add widgets to grid
        for i in range(self.num_of_widgets):
            widget_list[i].grid(row=i, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)

        # Save button
        self.btn_save = customtkinter.CTkButton(master=self, text="Save", font=button_med_font(), command=lambda: self.save(window=parent))
        self.btn_save.grid(row=self.num_of_widgets + 2, column=0, columnspan=2, pady=20, padx=20)

    def __modify_keybind(self):
        print("Modify keybind")
        self.btn_keybinds.configure(image=self.img_check)
        self.btn_keybinds.configure(command=self.__set_keybind)
        self.start_keyboard_listener()

    def __set_keybind(self):
        print("Set keybind")
        self.btn_keybinds.configure(image=self.img_edit)
        self.btn_keybinds.configure(command=self.__modify_keybind)
        self.stop_keyboard_listener()

    # ---- Keyboard Interrupt Handlers ----
    def start_keyboard_listener(self):
        self.listener = keyboard.Listener(
            on_press=self.__on_press,
            on_release=self.__on_release,
        )
        self.listener.start()

    def stop_keyboard_listener(self):
        with contextlib.suppress(AttributeError):
            self.listener.stop()

    def __on_press(self, key):
        if key in [keyboard.Key.esc]:
            self.entry_keybinds.configure(text="")
            self.current_keys.clear()
            return
        self.current_keys.add(key)
        self.entry_keybinds.configure(text=f"{settings.keybind_to_text(self.current_keys)}")

    def __on_release(self, key):
        pass

    def on_closing(self):
        self.stop_keyboard_listener()
        self.parent.destroy()

    def save(self, window):
        if not self.current_keys:
            settings.set("keybind", settings.default_keybind)
            print("No keybind set, using default keybind.")
        settings.set("keybind", self.current_keys)
        print(f"Keybind set to {settings.keybind_to_text(self.current_keys)}")
        print("Please restart OSBC for changes to take effect.")
        window.destroy()
