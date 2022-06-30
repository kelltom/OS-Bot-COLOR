

class CerberusController(object):
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

    def restart(self):
        '''
        Restart btn clicked on view.
        '''
        self.model.restart()

    def update(self):
        '''
        Update the view.
        '''
        self.view.update_status(self.model.status)
        progress = self.model.current_iter / self.model.iterations
        self.view.update_progress(progress)
