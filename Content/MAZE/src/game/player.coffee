PlayerState =
    DISABLED: 0
    INITIAL_PLACEMENT: 1
    IDLE: 2
    TURN: 3


playerPlacementReachDistance = 1
playerDefaultReachDistance = 4


class Player

    constructor: (index) ->
        @state = PlayerState.INITIAL_PLACEMENT
        @reachDistance = playerPlacementReachDistance
        @position = new Position()
        @index = index
