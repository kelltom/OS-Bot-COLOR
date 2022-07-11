from model.bot import Bot, BotStatus
from view.bot_view import BotView


class BotController(object):
    def __init__(self, model, view):
        '''
        Constructor.
        '''
        self.model: Bot = model
        self.view: BotView = view
        self.model.set_controller(self)

    def play_pause(self):
        '''
        Play/pause btn clicked on view.
        '''
        self.model.play_pause()

    def stop(self):
        '''
        Stop btn clicked on view.
        '''
        self.model.stop()

    def options_btn_clicked(self):
        '''
        Called from view. Preps model for configuring of options.
        '''
        self.model.set_status(BotStatus.CONFIGURING)
        self.update_status()
        self.view.frame_info.show_options()

    def save_options(self, options):
        '''
        Called from view. Tells model to save options.
        '''
        self.model.save_options(options)

    def abort_options(self):
        '''
        Called from view when options window is closed manually.
        '''
        self.update_log("Bot configuration aborted.")
        self.model.set_status(BotStatus.STOPPED)
        return

    def update_status(self):
        '''
        Called from model. Tells view to update status.
        '''
        status = self.model.status
        if status == BotStatus.RUNNING:
            self.view.frame_info.update_status_running()
        elif status == BotStatus.PAUSED:
            self.view.frame_info.update_status_paused()
        elif status == BotStatus.STOPPED:
            self.view.frame_info.update_status_stopped()
        elif status == BotStatus.CONFIGURING:
            self.view.frame_info.update_status_configuring()

    def update_progress(self):
        '''
        Called from model. Tells view to update progress.
        '''
        progress = self.model.current_iter / self.model.iterations
        self.view.frame_info.update_progress(progress)

    def update_log(self, msg: str, overwrite: bool = False):
        '''
        Called from model. Tells view to update log.
        '''
        self.view.frame_output_log.update_log(msg, overwrite)

    def clear_log(self):
        '''
        Called from model. Tells view to clear log.
        '''
        self.view.frame_output_log.clear_log()
