Direction =
    UP: 0
    RIGHT: 1
    DOWN: 2
    LEFT: 3

TileType =
    WALL: 0
    HALLWAY: 1
    BORDER: 2
    EMPTY: 3


class MazeEntry
    constructor: (@tileType = TileType.WALL, @tileIndex = 6) ->


class MazeModel

    constructor: ->
        @numberOfPlayers = 4

        @width = 32
        @height = 20

        @blackTileIndex = 5
        @transparentTileIndex = 6
        @wallTileIndex = 19
        @hallwayTileIndex = 7

    createRandomMaze: ->

        @placePlayers()

        # Create maze
        @resetMaze()
        @createMaze()

        # Set random tiles
        for y in [0..@height - 1]
            for x in [0..@width - 1]
                entry = @entryAtCoordinate(x, y)
                if entry.tileType == TileType.WALL or entry.tileType == TileType.BORDER
                    entry.tileIndex = @randomWallIndex()
                if entry.tileType == TileType.HALLWAY
                    entry.tileIndex = @randomHallwayIndex()
                if entry.tileType == TileType.EMPTY
                    entry.tileIndex = @transparentTileIndex

    resetMaze: ->
        @maze = ((new MazeEntry(@defaultTileTypeAtCoordinate(x, y)) for x in [0..@width - 1]) for y in [0..@height - 1])

    placePlayers: ->
        @players = (new Player() for _ in [1..@numberOfPlayers])

        @players[0].position = new Position(0, @height / 2)
        @players[1].position = new Position(@width - 1, @height / 2)
        @players[2].position = new Position(@width / 2, 0)
        @players[3].position = new Position(@width / 2, @height - 1)

    createMaze: ->

        # Reset list of positions to visit
        @positionsToVisit = []

        # Add hallway at players positions
        for player in @players
            @addHallwayAtPosition(player.position)

        # Build maze
        while @positionsToVisit.length > 0

            # Pick random position
            randomIndex = Util.randomInRange(0, @positionsToVisit.length)
            position = @positionsToVisit.splice(randomIndex, 1)[0]

            # Already used
            if @entryAtPosition(position).tileType == TileType.hallways
                continue

            # Find adjacent hallways
            adjacentHallways = []

            for adjacentPosition in @adjacentPositions(position)
                if @entryAtPosition(adjacentPosition).tileType == TileType.HALLWAY
                    adjacentHallways.push(adjacentPosition)

            if adjacentHallways.length != 1 then continue

            # Check hallway connection
            adjacentHallway = adjacentHallways[0]
            oppositePosition = new Position(position.x - (adjacentHallway.x - position.x), position.y - (adjacentHallway.y - position.y))

            if @entryAtPosition(position).tileType != TileType.WALL or @entryAtPosition(position).tileType != TileType.WALL
                continue

            if not @isPositionValid(oppositePosition, margin=1)
                continue

            # Add hallways
            @entryAtPosition(position).tileType = TileType.HALLWAY
            @addHallwayAtPosition(oppositePosition)

    addHallwayAtPosition: (position) ->
        @entryAtPosition(position).tileType = TileType.HALLWAY

        for adjacentPosition in @adjacentPositions(position)
            @addPositionToVisitList(adjacentPosition)

    addPositionToVisitList: (position) ->
        if @isPositionValid(position) and @entryAtPosition(position).tileType == TileType.WALL
            @positionsToVisit.push(position)

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

    adjacentHallwayPositions: (position) ->
        positions = @adjacentPositions(position)
        return (p for p in @adjacentPositions(position) when @entryAtPosition(p).tileType == TileType.HALLWAY)

    isPositionValid: (position, margin=0) -> position.x >= margin and position.y >= margin and position.x < @width - margin and position.y < @height - margin

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
            for adjacentPosition in @adjacentHallwayPositions(position)
                if distanceMap[adjacentPosition.y][adjacentPosition.x] == -1
                    distanceMap[adjacentPosition.y][adjacentPosition.x] = distance + 1
                    positionsToVisit.push(adjacentPosition)

        return positions

    randomWallIndex: -> return Util.randomInRange(@wallTileIndex, @wallTileIndex + 6)

    randomHallwayIndex: -> return Util.randomInRange(@hallwayTileIndex, @hallwayTileIndex + 6)

    entryAtCoordinate: (x, y) -> @maze[y][x]

    entryAtPosition: (position) -> @maze[position.y][position.x]

    defaultTileTypeAtCoordinate: (x, y) ->

        # Corners
        if (x == 0 and y == 0) or (x == 1 and y == 0) or (x == 0 and y == 1)
            return TileType.EMPTY
        if (x == 0 and y == @height - 1) or (x == 1 and y == @height - 1) or (x == 0 and y == @height - 2)
            return TileType.EMPTY
        if (x == @width - 1 and y == 0) or (x == @width - 2 and y == 0) or (x == @width - 1 and y == 1)
            return TileType.EMPTY
        if (x == @width - 1 and y == @height - 1) or (x == @width - 2 and y == @height - 1) or (x == @width - 1 and y == @height - 2)
            return TileType.EMPTY

        # Border
        if x == 0 or y == 0 or x == @width - 1 or y == @height - 1
            return TileType.BORDER
        if x == 1 and y == 1
            return TileType.BORDER
        if x == @width - 2 and y == 1
            return TileType.BORDER
        if x == 1 and y == @height - 2
            return TileType.BORDER
        if x == @width - 2 and y == @height - 2
            return TileType.BORDER

        # Anywhere else
        return TileType.WALL

    isBorder: (x, y) -> x == 0 or y == 0 or x == @width - 1 or y == @height - 1
