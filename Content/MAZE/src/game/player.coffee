PlayerState =
    DISABLED: 0
    INITIAL_PLACEMENT: 1
    IDLE: 2
    MOVING: 3


playerPlacementReachDistance = 3
playerDefaultReachDistance = 4


class Player

    constructor: ->
        @state = PlayerState.INITIAL_PLACEMENT
        @reachDistance = playerPlacementReachDistance
        @position = new Position()
