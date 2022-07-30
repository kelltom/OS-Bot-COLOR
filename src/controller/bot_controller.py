'''
Serves as the mediator between a bot and the UI. Methods should likely not be modified.
'''

from model.bot import Bot, BotStatus
from view.bot_view import BotView


class BotController(object):
    def __init__(self, model, view):
        '''
        Constructor.
        '''
        self.model: Bot = model
        self.view: BotView = view

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
        self.view.frame_info.show_options()

    def save_options(self, options):
        '''
        Called from view. Tells model to save options.
        '''
        self.model.save_options(options)
        self.model.set_status(BotStatus.STOPPED)

    def abort_options(self):
        '''
        Called from view when options window is closed manually.
        '''
        self.update_log("Bot configuration aborted.")
        self.model.set_status(BotStatus.STOPPED)

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

    def update_model(self, model: Bot):
        '''
        Called from view. Swaps the controller's model.
        '''
        if self.model is not None:
            self.model.stop()
        self.model = model
        if self.model is not None:
            self.view.frame_info.setup(title=model.title, description=model.description, options_class=model.options_class)
        else:
            self.view.frame_info.setup(title="", description="", options_class=None)
        self.clear_log()
