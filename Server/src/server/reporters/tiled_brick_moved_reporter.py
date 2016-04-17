from tiled_brick_position_reporter import TiledBrickPositionReporter


class TiledBrickMovedReporter(TiledBrickPositionReporter):
    def __init__(self, initial_location, valid_locations, stable_time):
        """
        :param initial_location Initial brick position
        :param valid_locations Locations to search for brick in
        :param stable_time Amount of time to wait for image to stabilize
        """
        super(TiledBrickMovedReporter, self).__init__(valid_locations, stable_time)
        self.initial_location = initial_location

    def is_location_ok(self, location):
        if not super(TiledBrickMovedReporter, self).is_location_ok(location):
            return False
        else:
            return location[0] != self.initial_location[0] or location[1] != self.initial_location[1]
