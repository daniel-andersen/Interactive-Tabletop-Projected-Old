from tiled_brick_position_reporter import TiledBrickPositionReporter


class TiledBrickMovedToAnyOfPositionsReporter(TiledBrickPositionReporter):
    def __init__(self, tiled_board_area, initial_position, valid_positions, stable_time, reporter_id, callback_function):
        """
        :param initial_position Initial brick position
        :param valid_positions Positions to search for brick in
        :param stable_time Amount of time to wait for image to stabilize
        """
        super(TiledBrickMovedToAnyOfPositionsReporter, self).__init__(tiled_board_area, valid_positions, stable_time, reporter_id, callback_function)
        self.initial_position = initial_position

    def is_position_ok(self, position):
        if not super(TiledBrickMovedToAnyOfPositionsReporter, self).is_position_ok(position):
            return False
        else:
            return position[0] != self.initial_position[0] or position[1] != self.initial_position[1]


class TiledBrickMovedToPositionReporter(TiledBrickPositionReporter):
    def __init__(self, tiled_board_area, position, valid_positions, stable_time, reporter_id, callback_function):
        """
        :param position Target brick position
        :param valid_positions Positions to search for brick in
        :param stable_time Amount of time to wait for image to stabilize
        """
        super(TiledBrickMovedToPositionReporter, self).__init__(tiled_board_area, valid_positions, stable_time, reporter_id, callback_function)
        self.target_position = position

    def is_position_ok(self, position):
        if not super(TiledBrickMovedToPositionReporter, self).is_position_ok(position):
            return False
        else:
            return position[0] == self.target_position[0] and position[1] == self.target_position[1]
