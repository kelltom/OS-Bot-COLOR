import random


class CerberusController(object):
    """
    CerberusController class.
    """

    def __init__(self, model, view):
        """
        Constructor.
        """
        self.model = model
        # The view itself is going to have internal functions that update the UI when called.
        # That's why we need a reference to it here, so that when the controller is done doing
        # its thing, it can tell the UI to update.
        self.view = view

    def run(self):
        """
        Run the controller.
        """
        pass

    def play(self):
        """
        Play btn clicked on view.
        """
        # generate random number between 1 and 100 and store it in a variable called progress
        progress = random.randint(1, 100)
        # update the progress bar on the view
        self.view.update_progress(progress)
