class Util
    @randomInRange: (min, max) -> Math.floor(Math.random() * (max - min) + min)


class Position
    constructor: (@x = 0, @y = 0) ->
