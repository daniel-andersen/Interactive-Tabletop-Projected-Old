import time
from threading import Thread


class Reporter(object):
    def __init__(self, reporter_id, callback_function):
        """
        :param reporter_id Reporter ID of this reporter.
        :param callback_function Callback function to call when done
        """
        self.stopped = True
        self.stopRequested = False
        self.reporter_id = reporter_id
        self.callback_function = callback_function

        print("Starting reporter: %i" % self.reporter_id)

    def start(self):
        self.stopped = False
        self.stopRequested = False

        thread = Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def stop(self):
        print("Stopping reporter: %i" % self.reporter_id)
        self.stopRequested = True

    def run(self):

        # Keep running until stopped
        while not self.stopRequested and not self.stopped:

            # Sleep a while
            time.sleep(0.01)

            # Update reporter
            self.update()

        print("Stopped reporter: %i" % self.reporter_id)
        self.stopped = True

    def update(self):
        pass
