class Screen(object):
    """
    Represents the description of the screen.

    width -- Width of screen
    height -- Height of screen
    """
    def __init__(self):
        self.width = 1280
        self.height = 800

    def __call__(self, *args, **kwargs):
        classname = type(self).__name__
        return globals()[classname]


screen = Screen()
