from tiled_brick_position_reporter import TiledBrickPositionReporter


class TiledBrickMovedReporter(TiledBrickPositionReporter):
    def __init__(self, initial_position, valid_positions, stable_time):
        """
        :param initial_position Initial brick position
        :param valid_positions Positions to search for brick in
        :param stable_time Amount of time to wait for image to stabilize
        """
        super(TiledBrickMovedReporter, self).__init__(valid_positions, stable_time)
        self.initial_position = initial_position

    def is_position_ok(self, position):
        if not super(TiledBrickMovedReporter, self).is_position_ok(position):
            return False
        else:
            return position[0] != self.initial_position[0] or position[1] != self.initial_position[1]
