WallType =
    UP: 1
    RIGHT: 2
    DOWN: 4
    LEFT: 8
    ALL_SIDES: 15
    BORDER: 16

blackTileIndex = 5
transparentTileIndex = 6
wallTileStartIndex = 7

class MazeEntry
    constructor: (@walls = [WallType.UP, WallType.RIGHT, WallType.DOWN, WallType.LEFT], @tileIndex = transparentTileIndex) ->

class MazeWall
    constructor: (@position1, @position2) ->

class MazeModel

    constructor: ->
        @numberOfPlayers = 4

        @width = 32
        @height = 20

    createRandomMaze: ->

        # Place players
        @placePlayers()

        # Create maze
        @resetMaze()
        @createMaze()
        @calculateTileIndices()

    resetMaze: ->
        @maze = ((new MazeEntry() for x in [1..@width]) for y in [1..@height])
        @validPositionMap = ((@isCoordinateValid(x, y) for x in [0..@width - 1]) for y in [0..@height - 1])

    placePlayers: ->
        @players = (new Player() for _ in [1..@numberOfPlayers])

        @players[0].position = new Position(@width / 2, 0)
        @players[1].position = new Position(@width - 1, @height / 2)
        @players[2].position = new Position(@width / 2, @height - 1)
        @players[3].position = new Position(0, @height / 2)

    createMaze: ->

        # Reset list of walls to visit
        @wallsToVisit = []

        # Remove walls at players positions and add to visit list
        adjacentPosition = new Position(@players[0].position.x, @players[0].position.y + 1)
        @removeWalls(@players[0].position, adjacentPosition)
        @addAdjacentWallsToVisitList(adjacentPosition)

        adjacentPosition = new Position(@players[1].position.x - 1, @players[1].position.y)
        @removeWalls(@players[1].position, adjacentPosition)
        @addAdjacentWallsToVisitList(adjacentPosition)

        adjacentPosition = new Position(@players[2].position.x, @players[2].position.y - 1)
        @removeWalls(@players[2].position, adjacentPosition)
        @addAdjacentWallsToVisitList(adjacentPosition)

        adjacentPosition = new Position(@players[3].position.x + 1, @players[3].position.y)
        @removeWalls(@players[3].position, adjacentPosition)
        @addAdjacentWallsToVisitList(adjacentPosition)

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

    calculateTileIndices: ->
        for y in [0..@height - 1]
            for x in [0..@width - 1]
                entry = @entryAtCoordinate(x, y)
                entry.tileIndex = @tileIndexAtCoordinate(x, y)

    removeWalls: (position1, position2) ->

        # Remove walls for position 1
        entry = @entryAtPosition(position1)
        wallType = @wallTypeOfAdjacentPositions(position1, position2)
        entry.walls = entry.walls.filter (type) -> type isnt wallType

        # Remove walls for position 2
        entry = @entryAtPosition(position2)
        wallType = @wallTypeOfAdjacentPositions(position2, position1)
        entry.walls = entry.walls.filter (type) -> type isnt wallType

    addAdjacentWallsToVisitList: (position) ->
        for adjacentPosition in @adjacentPositions(position)
            @wallsToVisit.push(new MazeWall(position, adjacentPosition))

    adjacentPositions: (position) ->
        positions = []

        p = new Position(position.x - 1, position.y)
        if @isPositionValid(p) then positions.push(p)

        p = new Position(position.x + 1, position.y)
        if @isPositionValid(p) then positions.push(p)

        p = new Position(position.x, position.y - 1)
        if @isPositionValid(p) then positions.push(p)

        p = new Position(position.x, position.y + 1)
        if @isPositionValid(p) then positions.push(p)

        return positions

    adjacentConnectedPositions: (position) ->
        return (p for p in @adjacentPositions(position) when @arePositionsConnected(position, p))

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
            for adjacentPosition in @adjacentConnectedPositions(position)
                if distanceMap[adjacentPosition.y][adjacentPosition.x] == -1
                    distanceMap[adjacentPosition.y][adjacentPosition.x] = distance + 1
                    positionsToVisit.push(adjacentPosition)

        return positions

    wallMaskAtPosition: (position) -> @entryAtPosition(position).walls.reduce( ((t, s) -> t + s), 0)

    entryAtCoordinate: (x, y) -> @maze[y][x]

    entryAtPosition: (position) -> @maze[position.y][position.x]

    arePositionsConnected: (position1, position2) ->
        wallType = @wallTypeOfAdjacentPositions(position1, position2)
        return wallType not in @entryAtPosition(position1).walls

    wallTypeOfAdjacentPositions: (position1, position2) ->

        # Horizontally adjacent
        if position1.y == position2.y
            if position1.x == position2.x - 1
                return WallType.RIGHT
            if position1.x == position2.x + 1
                return WallType.LEFT

        # Vertically adjacent
        if position1.x == position2.x
            if position1.y == position2.y - 1
                return WallType.DOWN
            if position1.y == position2.y + 1
                return WallType.UP

        return 0

    isCoordinateValid: (x, y) ->
        return not @isBorderAtCoordinate(x, y)

    isBorderAtCoordinate: (x, y) ->
        if x <= 0 or y <= 0 or x >= @width - 1 or y >= @height - 1 then return true
        if x == 1 and y == 1 then return true
        if x == @width - 2 and y == 1 then return true
        if x == 1 and y == @height - 2 then return true
        if x == @width - 2 and y == @height - 2 then return true
        return false

    tileIndexAtCoordinate: (x, y) ->
        entry = @entryAtCoordinate(x, y)
        return wallTileStartIndex + entry.walls.reduce( (((t, s) -> t + s)), 0)
