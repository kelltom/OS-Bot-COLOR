import customtkinter
from views.bot_view_components.info_frame import InfoFrame
from views.bot_view_components.output_log_frame import OutputLogFrame


class BotView(customtkinter.CTkFrame):
    def __init__(self, parent):
        '''
        A base frame for all bot views. This frame contains the following:
            - Info frame (frame_info)
            - Output log frame (frame_output_log)
        This view needs to be configured using setup() to populate fields based
        on the bot's title and description, as well as setting controllers for the child views.
        '''
        super().__init__(parent)

        # configure grid layout (3x1)
        self.rowconfigure(0, weight=0)  # info row will not resize
        self.rowconfigure(2, weight=1)  # log row will resize
        self.columnconfigure(0, weight=1)

        # ---------- TOP HALF (script info and control buttons) ----------
        self.frame_info = InfoFrame(parent=self, title="Title", info="Description")
        self.frame_info.grid(row=0, column=0, pady=15, padx=15, sticky="nsew")

        # ---------- BOTTOM HALF (log text box) ----------
        self.frame_output_log = OutputLogFrame(parent=self)
        self.frame_output_log.grid(row=2, column=0, pady=(0, 15), padx=15, sticky="nsew")

        self.controller = None

    def setup(self, controller, title, description):
        '''
        Sets up the view (and child views) with the given controller. Also sets the title and
        description for the info frame.
        '''
        self.controller = controller

        self.frame_info.set_controller(controller=controller)
        self.frame_info.setup(title=title, description=description)

        self.frame_output_log.set_controller(controller=controller)

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
        self.frame_output_log.update_log(msg=msg)

    def clear_log(self):
        '''
        Called from controller. Calls function of child view to clear log.
        '''
        self.frame_output_log.clear_log()
