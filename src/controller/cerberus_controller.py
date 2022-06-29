

class CerberusController(object):
    """
    CerberusController class.
    """

    def __init__(self, model, view):
        """
        Constructor.
        """
        self.model = model
        self.view = view

    def play(self):
        """
        Play btn clicked on view.
        """
        self.model.play()
        # # generate random number between 0 and 1 and store it in a variable called progress
        # progress = random.randint(0, 100)
        # # update the progress bar on the view
        # self.view.update_progress(progress/100.0)

    def stop(self):
        self.model.stop()

    # TODO:
    # I need a function that, when the bot is running, constantly checks a queue within the model for
    # messages to be sent to the view. This queue will be populated via the model's main loop.
    # The view will then update the progress bar and log accordingly.
