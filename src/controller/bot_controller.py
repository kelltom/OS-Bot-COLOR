from model.bot import BotStatus


class BotController(object):
    def __init__(self, model, view):
        '''
        Constructor.
        '''
        self.model = model
        self.view = view
        self.model.set_controller(self)

    def play_pause(self):
        '''
        Play/pause btn clicked on view.
        '''
        if self.model.status == BotStatus.STOPPED:
            settings = self.view.get_settings()
            self.model.save_settings(settings)
        self.model.play_pause()

    def stop(self):
        '''
        Stop btn clicked on view.
        '''
        self.model.stop()

    def restart(self):
        '''
        Restart btn clicked on view.
        '''
        settings = self.view.get_settings()
        self.model.save_settings(settings)
        self.model.restart()

    def update_status(self):
        '''
        Called from model. Tells view to update status.
        '''
        self.view.update_status(self.model.status)

    def update_progress(self):
        '''
        Called from model. Tells view to update progress.
        '''
        progress = self.model.current_iter / self.model.iterations
        self.view.update_progress(progress)

    def update_log(self, msg: str):
        '''
        Called from model. Tells view to update log.
        '''
        self.view.update_log(msg)

    def clear_log(self):
        '''
        Called from model. Tells view to clear log.
        '''
        self.view.clear_log()
