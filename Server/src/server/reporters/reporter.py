class Reporter(object):
    reporter_id = None
    callback_function = None
    stopped = False

    def __init__(self, reporter_id, callback_function):
        """
        :param reporter_id Reporter ID of this reporter.
        :param callback_function Callback function to call when done
        """
        self.stopped = False
        self.reporter_id = reporter_id
        self.callback_function = callback_function

        print("Starting reporter: %i" % self.reporter_id)

    def stop(self):
        print("Stopping reporter: %i" % self.reporter_id)
        self.stopped = True

    def run_iteration(self):
        """
        Method called for each iteration. Should be overridden.
        """
        pass
