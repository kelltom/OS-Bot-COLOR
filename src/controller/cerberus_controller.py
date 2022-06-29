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
        self.view = view

    def play(self):
        """
        Play btn clicked on view.
        """
        # generate random number between 0 and 1 and store it in a variable called progress
        progress = random.randint(0, 100)
        # update the progress bar on the view
        self.view.update_progress(progress/100.0)
