

class BotController(object):
    def __init__(self, model, view):
        '''
        Constructor.
        '''
        self.model = model
        self.view = view
        self.model.set_controller(self)

    def play_pause(self, settings: dict):
        '''
        Play/pause btn clicked on view.
        '''
        self.__save_settings(settings)
        self.model.play_pause()

    def stop(self):
        '''
        Stop btn clicked on view.
        '''
        self.model.stop()

    def restart(self, settings: dict):
        '''
        Restart btn clicked on view.
        '''
        self.__save_settings(settings)
        self.model.restart()

    # TODO: Maybe divide this function to reduce redundancy
    def update(self):
        '''
        Called from model. Tells view to update.
        '''
        self.view.update_status(self.model.status)
        progress = self.model.current_iter / self.model.iterations
        self.view.update_progress(progress)

    def __save_settings(self, settings: dict):
        '''
        Private function, saves settings from a dict to the model.
        '''
        # TODO: iterate through all settings and save them to the model
        pass
