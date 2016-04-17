WallType =
    UP: 1
    RIGHT: 2
    DOWN: 4
    LEFT: 8
    ALL_SIDES: 15

Direction =
    UP: 0
    RIGHT: 1
    DOWN: 2
    LEFT: 3

directionMovements = [[0, -1], [1, 0], [0, 1], [-1, 0]]

blackTileIndex = 5
transparentTileIndex = 6
wallTileStartIndex = 7
darkenTileOffset = 20

class MazeEntry
    constructor: (@walls = [WallType.UP, WallType.RIGHT, WallType.DOWN, WallType.LEFT], @tileIndex = transparentTileIndex) ->

class MazeWall
    constructor: (@position1, @position2) ->

class MazeModel

    constructor: ->
        @numberOfPlayers = 4

        @width = 32
        @height = 20

        @granularity = 2

    createRandomMaze: ->

        # Place players
        @placePlayers()

        # Create maze
        @resetMaze()
        @createMaze()
        @calculateTileIndices()

    resetMaze: ->

        # Reset maze
        @maze = ((new MazeEntry() for x in [1..@width]) for y in [1..@height])
        @validPositionMap = ((@isCoordinateValid(x, y) for x in [0..@width - 1]) for y in [0..@height - 1])

        # Prevent hallways at players adjacent border tiles
        @validPositionMap[@players[0].position.y][@players[0].position.x - @granularity] = false
        @validPositionMap[@players[0].position.y][@players[0].position.x + @granularity] = false

        @validPositionMap[@players[1].position.y - @granularity][@players[1].position.x] = false
        @validPositionMap[@players[1].position.y + @granularity][@players[1].position.x] = false

        @validPositionMap[@players[2].position.y][@players[2].position.x - @granularity] = false
        @validPositionMap[@players[2].position.y][@players[2].position.x + @granularity] = false

        @validPositionMap[@players[3].position.y - @granularity][@players[3].position.x] = false
        @validPositionMap[@players[3].position.y + @granularity][@players[3].position.x] = false

    placePlayers: ->
        @players = (new Player(i) for i in [0..@numberOfPlayers - 1])

        @players[0].position = new Position(@width / 2, 0)
        @players[1].position = new Position(@width - 1, @height / 2)
        @players[2].position = new Position(@width / 2, @height - 1)
        @players[3].position = new Position(0, @height / 2)

    createMaze: ->

        # Reset list of walls to visit
        @wallsToVisit = []

        # Remove walls at random starting position
        position = @positionWithGranularity(new Position(@width / 2, @height / 2))
        @removeWalls(position, new Position(position.x + 1, position.y))
        @addAdjacentWallsToVisitList(position)

        # Build maze
        while @wallsToVisit.length > 0

            # Pick random position
            randomIndex = Util.randomInRange(0, @wallsToVisit.length)
            wall = @wallsToVisit.splice(randomIndex, 1)[0]

            # There must exist exactly one visited tile on either side of the wall
            if @wallMaskAtPosition(wall.position1) != WallType.ALL_SIDES and @wallMaskAtPosition(wall.position2) != WallType.ALL_SIDES
                continue

            # Remove walls
            @removeWalls(wall.position1, wall.position2)

            # Add adjacent positions
            @addAdjacentWallsToVisitList(wall.position2)

        # Dig walls to players
        @digWalls(@players[0].position, Direction.DOWN, stop=WallType.ALL_SIDES)
        @digWalls(@players[1].position, Direction.LEFT, stop=WallType.ALL_SIDES)
        @digWalls(@players[2].position, Direction.UP, stop=WallType.ALL_SIDES)
        @digWalls(@players[3].position, Direction.RIGHT, stop=WallType.ALL_SIDES)

        # Dig walls to "non-granularity" tiles
        for y in [0..@height - 1]
            for x in [0..@width - 1]
                position = new Position(x, y)
                entry = @entryAtPosition(position)

                upPosition = new Position(x, y - 1)
                if @isPositionValid(upPosition) and WallType.DOWN not in @entryAtPosition(upPosition).walls
                    entry.walls = entry.walls.filter (type) -> type isnt WallType.UP

                rightPosition = new Position(x + 1, y)
                if @isPositionValid(rightPosition) and WallType.LEFT not in @entryAtPosition(rightPosition).walls
                    entry.walls = entry.walls.filter (type) -> type isnt WallType.RIGHT

                downPosition = new Position(x, y + 1)
                if @isPositionValid(downPosition) and WallType.UP not in @entryAtPosition(downPosition).walls
                    entry.walls = entry.walls.filter (type) -> type isnt WallType.DOWN

                leftPosition = new Position(x - 1, y)
                if @isPositionValid(leftPosition) and WallType.RIGHT not in @entryAtPosition(leftPosition).walls
                    entry.walls = entry.walls.filter (type) -> type isnt WallType.LEFT

    calculateTileIndices: ->
        for y in [0..@height - 1]
            for x in [0..@width - 1]
                entry = @entryAtCoordinate(x, y)
                entry.tileIndex = @tileIndexAtCoordinate(x, y)

    removeWalls: (position1, position2, granularity=@granularity) ->

        # Remove walls for position 1
        entry = @entryAtPosition(position1)
        wallType = @wallTypeOfAdjacentPositions(position1, position2, granularity)
        entry.walls = entry.walls.filter (type) -> type isnt wallType

        # Remove walls for position 2
        entry = @entryAtPosition(position2)
        wallType = @wallTypeOfAdjacentPositions(position2, position1, granularity)
        entry.walls = entry.walls.filter (type) -> type isnt wallType

    addAdjacentWallsToVisitList: (position, granularity=@granularity) ->
        for adjacentPosition in @adjacentPositions(position, granularity)
            @wallsToVisit.push(new MazeWall(position, adjacentPosition))

    adjacentPositions: (position, granularity=@granularity) ->
        positions = []

        p = new Position(position.x - granularity, position.y)
        if @isPositionValid(p) then positions.push(p)

        p = new Position(position.x + granularity, position.y)
        if @isPositionValid(p) then positions.push(p)

        p = new Position(position.x, position.y - granularity)
        if @isPositionValid(p) then positions.push(p)

        p = new Position(position.x, position.y + granularity)
        if @isPositionValid(p) then positions.push(p)

        return positions

    adjacentConnectedPositions: (position, granularity=@granularity) ->
        return (p for p in @adjacentPositions(position, granularity) when @arePositionsConnected(position, p, granularity))

    isPositionValid: (position) ->
        if position.x < 0 or position.y < 0 or position.x > @width - 1 or position.y > @height - 1 then return false
        return @validPositionMap[position.y][position.x]

    positionsReachableByPlayer: (player) -> @positionsReachableFromPosition(player.position, player.reachDistance)

    positionsReachableFromPosition: (position, maxDistance) ->

        # Clear distance map
        distanceMap = ((-1 for _ in [1..@width]) for _ in [1..@height])
        distanceMap[position.y][position.x] = 0

        # Reset positions
        positions = []
        positionsToVisit = [position]

        # Keep expanding until reach distance reached for all positions to visit
        while positionsToVisit.length > 0
            position = positionsToVisit.splice(0, 1)[0]
            distance = distanceMap[position.y][position.x]

            if distance >= maxDistance
                continue

            # Add to reachable positions
            positions.push(position)

            # Visit all adjacent positions that has not yet been visited
            for adjacentPosition in @adjacentConnectedPositions(position, granularity = 1)
                if distanceMap[adjacentPosition.y][adjacentPosition.x] == -1
                    distanceMap[adjacentPosition.y][adjacentPosition.x] = distance + 1
                    positionsToVisit.push(adjacentPosition)

        return positions

    digWalls: (position, direction, stop=WallType.ALL_SIDES) ->
        entry = @entryAtPosition(position)

        while @wallMaskAtPosition(position) != WallType.ALL_SIDES
            nextPosition = @positionInDirection(position, direction)
            if not @isPositionValid(nextPosition) then return

            @removeWalls(position, nextPosition, granularity=1)

            position = nextPosition
            entry = @entryAtPosition(nextPosition)

    positionInDirection: (position, direction) -> new Position(position.x + directionMovements[direction][0], position.y + directionMovements[direction][1])

    wallMaskAtPosition: (position) -> @entryAtPosition(position).walls.reduce( ((t, s) -> t + s), 0)

    entryAtCoordinate: (x, y) -> @maze[y][x]

    entryAtPosition: (position) -> @maze[position.y][position.x]

    arePositionsConnected: (position1, position2, granularity=@granularity) ->
        wallType = @wallTypeOfAdjacentPositions(position1, position2, granularity)
        return wallType not in @entryAtPosition(position1).walls

    wallTypeOfAdjacentPositions: (position1, position2, granularity=@granularity) ->

        # Horizontally adjacent
        if position1.y == position2.y
            if position1.x == position2.x - granularity
                return WallType.RIGHT
            if position1.x == position2.x + granularity
                return WallType.LEFT

        # Vertically adjacent
        if position1.x == position2.x
            if position1.y == position2.y - granularity
                return WallType.DOWN
            if position1.y == position2.y + granularity
                return WallType.UP

        return 0

    isCoordinateValid: (x, y) ->
        return not @isBorderAtCoordinate(x, y)

    isBorderAtCoordinate: (x, y) ->

        # Do not occupy corner markers
        if x <= 1 and y <= 1 then return true
        if x >= @width - 2 and y <= 1 then return true
        if x <= 1 and y >= @height - 2 then return true
        if x >= @width - 2 and y >= @height - 2 then return true

        return false

    tileIndexAtCoordinate: (x, y) ->
        entry = @entryAtCoordinate(x, y)
        return wallTileStartIndex + entry.walls.reduce( (((t, s) -> t + s)), 0)

    positionWithGranularity: (position, granularity=@granularity) -> new Position(position.x - (position.x % granularity), position.y - (position.y % granularity))
