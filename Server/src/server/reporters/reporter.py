from threading import Thread


class Reporter(object):
    reporter_id = None
    callback_function = None
    stopped = False

    def start(self, reporter_id, callback_function):
        """
        Starts a new reporter.

        :param reporter_id Reporter ID of this reporter.
        :param callback_function Callback function to call when done
        """
        self.stopped = False
        self.reporter_id = reporter_id
        self.callback_function = callback_function

        Thread(target=self.run, args=()).start()

    def stop(self):
        self.stopped = True

    def run(self):
        """
        Method called when thread starts. Should be overridden.
        """
        pass
