

class CerberusController(object):
    def __init__(self, model, view):
        '''
        Constructor.
        '''
        self.model = model
        self.view = view

    def play_pause(self):
        '''
        Play/pause btn clicked on view.
        '''
        self.model.play_pause()
        self.view.update_status(self.model.status)

    def stop(self):
        '''
        Stop btn clicked on view.
        '''
        self.model.stop()
        self.view.update_status(self.model.status)

    def restart(self):
        '''
        Restart btn clicked on view.
        '''
        self.model.restart()
        self.view.update_status(self.model.status)

    # TODO:
    # I need a function that, when the bot is running, constantly checks a queue within the model for
    # messages to be sent to the view. This queue will be populated via the model's main loop.
    # The view will then update the progress bar and log accordingly.
