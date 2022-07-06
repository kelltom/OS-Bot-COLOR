

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
        self.model.play_pause()

    def stop(self):
        '''
        Stop btn clicked on view.
        '''
        self.model.stop()

    def set_options(self):
        '''
        Options btn clicked on view.
        '''
        self.model.set_options()

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

    def update_log(self, msg: str, overwrite: bool = False):
        '''
        Called from model. Tells view to update log.
        '''
        self.view.update_log(msg, overwrite)

    def clear_log(self):
        '''
        Called from model. Tells view to clear log.
        '''
        self.view.clear_log()
