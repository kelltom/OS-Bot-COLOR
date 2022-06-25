'''
Should provide the view(s) to be returned to the main view.
Should also use the script1_controller.
'''

import customtkinter
import tkinter
from PIL import Image, ImageTk  # <- import PIL for the images
import pathlib

PATH = pathlib.Path(__file__).parent.parent.resolve()


class CerberusView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # configure grid layout (3x7)
        self.rowconfigure((0, 1, 2, 3), weight=0)  # first 4 rows will not resize
        self.rowconfigure(7, weight=10)  # big spacing for row 7 (heavier weight means it'll use more extra space than other components)
        self.columnconfigure((0, 1), weight=1)  # first 2 cols will resize
        self.columnconfigure(2, weight=0)  # last column will remain the size required to fit its contents

        # ------- first two columns -------
        # script info box
        self.frame_info = customtkinter.CTkFrame(master=self)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="This is the Cerberus script,\n" +
                                                        "choose number of iterations\n" +
                                                        "and then press play.",
                                                   height=100,
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, columnspan=2, row=0, rowspan=3, sticky="nwes", padx=15, pady=15)

        # -- script info box progress bar
        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        self.progressbar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=15, pady=15)

        # -- script iteration selector frame with + and - buttons
        self.iteration_frame = customtkinter.CTkFrame(master=self)
        self.iteration_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=15)
        self.iteration_frame.rowconfigure(0, weight=1)
        self.iteration_frame.columnconfigure((0, 2), weight=1)
        self.iteration_frame.columnconfigure(1, weight=1)
        # ---- slider
        self.slider_1 = customtkinter.CTkSlider(master=self.iteration_frame,
                                                from_=0,
                                                to=1,
                                                number_of_steps=100,
                                                command=self.progressbar.set)
        self.slider_1.grid(row=0, column=1, sticky="we")
        # ---- slider buttons
        image_size = 20
        plus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/plus.png").resize((image_size, image_size)))
        minus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/minus.png").resize((image_size, image_size)))
        self.decrement_button = customtkinter.CTkButton(master=self.iteration_frame,
                                                        text="",
                                                        image=minus_image)
        self.increment_button = customtkinter.CTkButton(master=self.iteration_frame,
                                                        text="",
                                                        image=plus_image)
        self.decrement_button.grid(row=0, column=0)
        self.increment_button.grid(row=0, column=2)
