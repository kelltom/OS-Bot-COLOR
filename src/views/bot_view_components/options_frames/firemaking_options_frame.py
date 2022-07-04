import customtkinter
import tkinter
from views.bot_view_components.options_frames.abstract_options import AbstractOptions


class FiremakingOptionsFrame(customtkinter.CTkFrame, AbstractOptions):
    def __init__(self, parent):
        super().__init__(master=parent)

        self.rowconfigure(0, weight=1)

        self.firemaking_options_label = customtkinter.CTkLabel(master=self,
                                                               text="FM Options",
                                                               justify=tkinter.LEFT,
                                                               text_font=("default_theme", 12))
        self.firemaking_options_label.grid(row=0, column=0, sticky="wns", padx=15, pady=15)

        # # ------- script configuration options -------
        # # -- script iterations
        # self.iteration_label = customtkinter.CTkLabel(master=self,
        #                                               text="Number of iterations:",
        #                                               justify=tkinter.LEFT)
        # self.iteration_label.grid(row=5, column=0, padx=15, pady=15)
        # self.iteration_select_frame = customtkinter.CTkFrame(master=self)
        # self.iteration_select_frame.columnconfigure((0, 2), weight=1)
        # self.iteration_select_frame.columnconfigure(1, weight=10)
        # self.iteration_select_frame.grid(row=5, column=1, padx=15, pady=15)
        # # ---- iterations manual entry
        # self.iterations_entry = customtkinter.CTkEntry(master=self.iteration_select_frame,
        #                                                width=40,
        #                                                placeholder_text="100")
        # self.iterations_entry.grid(row=0, column=1, sticky="we")
        # # ---- iterations increment/decrement buttons
        # image_size = 20
        # plus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/plus.png").resize((image_size, image_size)))
        # minus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/minus.png").resize((image_size, image_size)))
        # self.iteration_decrement_button = customtkinter.CTkButton(master=self.iteration_select_frame,
        #                                                           text="",
        #                                                           image=minus_image,
        #                                                           width=20,
        #                                                           fg_color=("gray75", "gray30"))
        # self.iteration_increment_button = customtkinter.CTkButton(master=self.iteration_select_frame,
        #                                                           text="",
        #                                                           image=plus_image,
        #                                                           width=20,
        #                                                           fg_color=("gray75", "gray30"))
        # self.iteration_decrement_button.grid(row=0, column=0)
        # self.iteration_increment_button.grid(row=0, column=2)

    def set_controller(self, controller):
        self.controller = controller

    def get_options(self):
        pass
