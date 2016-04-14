class Util
    @randomInRange: (min, max) -> Math.floor(Math.random() * (max - min) + min)


class Position
    constructor: (@x = 0, @y = 0) ->

    equals: (position) -> @x == position.x and @y == position.y
