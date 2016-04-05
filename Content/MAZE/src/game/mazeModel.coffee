TileType =
    WALL: 0
    HALLWAY: 1


class MazeEntry

    constructor: (@tileType = TileType.WALL) ->


class MazeModel

    constructor: ->
        @numberOfPlayers = 4

        @width = 32
        @height = 20

        @playerDefaultReachDistance = 4
        @playerReachDistance = [@playerDefaultReachDistance for _ in [1..@numberOfPlayers]]

        @granularity = 2
        @wallMinLength = 2
        @wallMaxLength = 3

    createRandomMaze: ->
        @resetMaze()

    resetMaze: ->
        @maze = [[new MazeEntry(if @isBorder(x, y) then TileType.WALL else TileType.HALLWAY) for x in [0..(@width - 1)]] for y in [0..(@height - 1)]]

    isBorder: (x, y) -> x == 0 or y == 0 or x == @width - 1 or y == @height - 1
