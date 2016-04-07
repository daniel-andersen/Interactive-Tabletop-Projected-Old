Direction =
    UP: 0
    RIGHT: 1
    DOWN: 2
    LEFT: 3

TileType =
    WALL: 0
    HALLWAY: 1


class MazeEntry
    constructor: (@tileType = TileType.WALL) ->


class MazeModel

    constructor: ->
        @numberOfPlayers = 4

        @players = (new Player() for i in [1..@numberOfPlayers])

        @width = 32
        @height = 20

        @granularity = 2
        @wallMinLength = 2
        @wallMaxLength = 3

    createRandomMaze: ->
        # Try at most 10 times to place treasure
        for _ in [1..10]

            # Create maze
            @resetMaze()
            @placePlayers()
            @createWalls()

            # Everything fine
            return

    resetMaze: ->
        @maze = ((new MazeEntry(if @isBorder(x, y) then TileType.WALL else TileType.HALLWAY) for x in [0..(@width - 1)]) for y in [0..(@height - 1)])

    placePlayers: ->
        @players[0].position = new Position(0, @height / 2)
        @players[1].position = new Position(@width - 1, @height / 2)
        @players[2].position = new Position(@width / 2, 0)
        @players[3].position = new Position(@width / 2, @height - 1)

    createWalls: ->
        numberOfWalls = (@width * 2 / 3) * @height

        for i in [1..numberOfWalls]
            @attemptWallStart()

        for player in @players
            alert(player.position.y)
            @entryAtPosition(player.position).tileType = TileType.HALLWAY

    attemptWallStart: ->
        @attemptWallStartAtPosition @randomWallStart()

    attemptWallStartAtPosition: (position) ->
        entry = @entryAtPosition(position)
        if entry.tileType == TileType.WALL
            return

        direction = Util.randomInRange(0, 4)
        length = (Util.randomInRange(@wallMinLength, @wallMaxLength + 1) * @granularity) + 1

        @createWall(position, direction, length)

    createWall: (position, direction, length) ->
        stepX = if direction == Direction.LEFT then -1 else (if direction == Direction.RIGHT then 1 else 0)
        stepY = if direction == Direction.UP   then -1 else (if direction == Direction.DOWN  then 1 else 0)

        for i in [1..length]
            entry = @entryAtPosition(position)
            if entry.tileType == TileType.WALL
                return

            entry.tileType = TileType.WALL
            position.x += stepX
            position.y += stepY

    randomWallStart: ->
        return new Position(Util.randomInRange(0, @width), Util.randomInRange(0, @height))

    entryAtPosition: (position) -> @maze[position.y][position.x]

    isBorder: (x, y) -> x == 0 or y == 0 or x == @width - 1 or y == @height - 1
