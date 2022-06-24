'''
Should provide the view(s) to be returned to the main view.
Should also use the script1_controller.
'''
import customtkinter
import tkinter


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
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

        # -- script info box progress bar and slider
        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        self.progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=15)
        self.slider_1 = customtkinter.CTkSlider(master=self,
                                                from_=0,
                                                to=1,
                                                number_of_steps=100,
                                                command=self.progressbar.set)
        self.slider_1.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="we")
