'''
Should provide the view(s) to be returned to the main view.
Should also use the script1_controller.
'''

import customtkinter
from views.reusable_views.info_frame import InfoFrame
from views.reusable_views.output_log_frame import OutputLogFrame


class FiremakingView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # configure grid layout (3x1)
        self.rowconfigure(0, weight=0)  # info row will not resize
        self.rowconfigure(1, weight=1)  # settings row will resize
        self.rowconfigure(2, weight=1)  # log row will resize but take more space
        self.columnconfigure(0, weight=1)

        # ---------- TOP HALF (script info and control buttons) ----------
        info_text = ("This is just me typing about the script and this text should wrap " +
                     "according to the length of the label. I'm just gonna keep typing to " +
                     "make this a really long label.")
        self.frame_info = InfoFrame(parent=self, title="Firemaking", info=info_text)
        self.frame_info.grid(row=0, column=0, pady=15, padx=15, sticky="nsew")

        # ---------- BOTTOM HALF (log text box) ----------
        self.output_log = OutputLogFrame(parent=self)
        self.output_log.grid(row=2, column=0, pady=15, padx=15, sticky="nsew")

        self.controller = None

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
        '''
        Sets the controller of this view, as well as the controller of the child view(s).
        '''
        self.controller = controller
        self.frame_info.set_controller(controller=controller)
        self.output_log.set_controller(controller=controller)

    def get_settings(self) -> dict:
        '''
        Extracts all settings from view to a dictionary.
        '''
        return {}

    def update_status(self, status):
        '''
        Called from controller. Calls function of child view to update status.
        '''
        self.frame_info.update_status(status=status)

    def update_progress(self, progress):
        '''
        Called from controller. Calls function of child view to update progress.
        '''
        self.frame_info.update_progress(progress=progress)

    def update_log(self, msg):
        '''
        Called from controller. Calls function of child view to update log.
        '''
        self.output_log.update_log(msg=msg)

    def clear_log(self):
        '''
        Called from controller. Calls function of child view to clear log.
        '''
        self.output_log.clear_log()
