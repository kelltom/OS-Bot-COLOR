from threading import Thread


class CerberusController(object):
    def __init__(self, model, view):
        '''
        Constructor.
        '''
        self.model = model
        self.view = view
        self.should_poll = False
        self.thread = None

    def poll(self):
        '''
        Poll the model for data.
        '''
        while self.should_poll:
            # Check if there is data in the queue.
            if self.model.queue.qsize() > 0:
                # Get the data from the queue.
                data = self.model.queue.get()
                # Determine if data is a status update or a script output.
                if data[0] == 'status':
                    # Update the status on the view.
                    self.view.update_status(data[1])
                    if data[1] in [3, 4]:  # Stopped or Idle
                        self.should_poll = False
                elif data[0] == 'output':
                    # Update the log on the view.
                    self.view.update_log(data[1])

    def play_pause(self):
        '''
        Play/pause btn clicked on view.
        '''
        prev_status = self.model.status
        self.model.play_pause()
        self.view.update_status(self.model.status)  # TODO: Remove
        self.should_poll = True
        # If the bot was stopped or idle, start a new thread,
        # as the old thread will be dead.
        if prev_status in [3, 4]:
            self.thread = Thread(target=self.poll)
            self.thread.start()

    def stop(self):
        '''
        Stop btn clicked on view.
        '''
        self.model.stop()
        # TODO: Remove
        self.view.update_status(self.model.status)
        self.should_poll = False

    def restart(self):
        '''
        Restart btn clicked on view.
        '''
        self.model.restart()
        self.view.update_status(self.model.status)  # TODO: Remove
        # TODO: Verify this code. Should I be restarting the thread? Will the old thread die?
        self.thread = Thread(target=self.poll)
        self.thread.start()
