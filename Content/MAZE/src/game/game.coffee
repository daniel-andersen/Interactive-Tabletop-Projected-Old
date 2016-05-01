MAZE = MAZE or {}
MAZE.Game = new Kiwi.State("Game")

tileLayers = []

mazeGame = null

MAZE.Game.preload = ->
    @addJSON("tilemap", "assets/maps/maze.json")
    @addSpriteSheet("tiles", "assets/img/tiles/board_tiles.png", 40, 40)
    @addImage("logo", "assets/img/menu/title.png")
    @addImage("treasure", "assets/img/tiles/treasure.png")

MAZE.Game.create = ->
    Kiwi.State::create.call(this)

    mazeGame = new MazeGame(this)
    mazeGame.start()

MAZE.Game.shutDown = ->
    Kiwi.State::shutDown.call(this)
    mazeGame.stop()

MAZE.Game.update = ->
    Kiwi.State::update.call(this)



GameState =
    INITIALIZING: 0
    INITIAL_PLACEMENT: 1
    PLAYING_GAME: 2



class MazeGame

    constructor: (@kiwiState) ->
        @client = new Client()
        @mazeModel = new MazeModel()

    start: ->
        @setupUi()
        @startNewGame()

        @client.connect((() => @reset()), ((json) => @onMessage(json)))

    stop: ->
        @client.disconnect()

    reset: ->
        @client.reset(resolution=[1280, 960])
        @client.enableDebug()

    onMessage: (json) ->
        switch json["action"]
            when "reset" then @initializeBoard()
            when "initializeTiledBoard" then @ready()
            when "brickFoundAtPosition" then @brickFoundAtPosition(payload=json["payload"])
            when "brickMovedToPosition" then @brickMovedToPosition(payload=json["payload"])



    startNewGame: ->

        # Prepare game state
        @gameState = GameState.INITIALIZING

        # Prepare map
        @visibleLayer = 0

        @tileLayers[0].alpha = 0.0
        @tileLayers[1].alpha = 0.0

        @treasure.alpha = 0.0

        @resetMaze()

        # Fade logo
        setTimeout(() =>
            fadeLogoTween = @kiwiState.game.tweens.create(@logo);
            fadeLogoTween.to({ alpha: 1.0 }, 2000, Kiwi.Animations.Tweens.Easing.Linear.In, true)
        , 500)

    setupUi: ->

        # Show canvas
        content = document.getElementById("content")
        content.style.visibility = "visible"

        # Setup logo
        @logo = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.logo, 0, 0)
        @logo.alpha = 0.0

        # Setup treasure
        @treasure = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.treasure, 0, 0)
        @treasure.alpha = 0.0
        @treasure.anchorPointX = 0.0
        @treasure.anchorPointY = 0.0

        # Setup tilemap
        @tilemap = new Kiwi.GameObjects.Tilemap.TileMap(@kiwiState, "tilemap", @kiwiState.textures.tiles)
        @borderLayer = @tilemap.getLayerByName("Border Layer")

        @tileLayers = []
        @tileLayers.push(@tilemap.getLayerByName("Tile Layer 1"))
        @tileLayers.push(@tilemap.getLayerByName("Tile Layer 2"))

        # Add elements to UI
        @kiwiState.addChild(@borderLayer)
        @kiwiState.addChild(@tileLayers[0])
        @kiwiState.addChild(@tileLayers[1])
        @kiwiState.addChild(@treasure)
        @kiwiState.addChild(@logo)

        # Setup debug log
        ###
        statusTextField = new Kiwi.HUD.Widget.TextField(@kiwiState.game, "", 100, 10)
        statusTextField.style.color = "#00ff00"
        statusTextField.style.fontSize = "14px"
        statusTextField.style.textShadow = "-1px -1px 5px black, 1px -1px 5px black, -1px 1px 5px black, 1px 1px 5px black"
        @client.debug_textField = statusTextField
        @kiwiState.game.huds.defaultHUD.addWidget(statusTextField)
        ###



    initializeBoard: ->
        @client.initializeTiledBoard(@mazeModel.width, @mazeModel.height)

    waitForStartPositions: ->
        for player in @mazeModel.players
            @requestPlayerInitialPosition(player)

    brickFoundAtPosition: (payload) ->
        player = @mazeModel.players[payload["id"]]
        position = new Position(payload["position"][0], payload["position"][1])
        @playerPlacedInitialBrick(player, position)

    brickMovedToPosition: (payload) ->
        player = @mazeModel.players[payload["id"]]
        position = new Position(payload["position"][0], payload["position"][1])

        switch @gameState
            when GameState.INITIAL_PLACEMENT
                if position.equals(player.position)
                    @playerPlacedInitialBrick(player, position)
                else
                    @playerMovedInitialBrick(player, position)
            when GameState.PLAYING_GAME
                if player.index == @currentPlayer.index
                    @playerMovedBrick(position)

    playerPlacedInitialBrick: (player, position) ->
        player.state = PlayerState.IDLE
        player.reachDistance = playerDefaultReachDistance
        @updateMaze()

        # Start brick move reporter
        setTimeout(() =>
            @requestPlayerPosition(player)
        , 1500)

    playerMovedInitialBrick: (player, position) ->

        # Disable players with no brick placed
        for aPlayer in @mazeModel.players
            if aPlayer.state != PlayerState.IDLE
                aPlayer.state = PlayerState.DISABLED

        # Get starting playing game
        @gameState = GameState.PLAYING_GAME

        # Fade logo away
        fadeLogoTween = @kiwiState.game.tweens.create(@logo);
        fadeLogoTween.to({ alpha: 0.0 }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true)

        # Show treasure
        p = @positionOnMap(@mazeModel.treasurePosition.x, @mazeModel.treasurePosition.y)
        @treasure.x = p.x
        @treasure.y = p.y

        setTimeout(() =>
            fadeTreasureTween = @kiwiState.game.tweens.create(@treasure);
            fadeTreasureTween.to({ alpha: 1.0 }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true)
        , 1000)

        # Move player
        player.state = PlayerState.TURN
        @currentPlayer = player

        @playerMovedBrick(position)

    playerMovedBrick: (position) ->

        # Reset reporters
        @client.resetReporters()

        # Move player
        oldPosition = @currentPlayer.position
        @currentPlayer.position = position
        @updateMaze()

        # Check finished
        if @currentPlayer.position.equals(@mazeModel.treasurePosition)
            @playerDidFindTreasure(oldPosition)
        else
            @nextPlayerTurn()

    playerDidFindTreasure: (fromPosition) ->

        # Animate treasure to former position
        setTimeout(() =>
            p = @positionOnMap(fromPosition.x, fromPosition.y)
            moveTreasureTween = @kiwiState.game.tweens.create(@treasure);
            moveTreasureTween.to({ x: p.x, y: p.y }, 1000, Kiwi.Animations.Tweens.Easing.Quadratic.InOut, true)
        , 1000)

        # Disappear
        setTimeout(() =>

            # Disable players
            for player in @mazeModel.players
                player.state = PlayerState.DISABLED

            # Fade treasure
            fadeTreasureTween = @kiwiState.game.tweens.create(@treasure);
            fadeTreasureTween.to({ alpha: 0.0 }, 2000, Kiwi.Animations.Tweens.Easing.Linear.In, true)

            # Clear maze
            @clearMaze()
            @updateMaze()
        , 4000)

        # Restart game
        setTimeout(() =>
            @startNewGame()
            @reset()
        , 7000)

    requestPlayerInitialPosition: (player) ->
        positions = ([position.x, position.y] for position in @mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2))
        @client.reportBackWhenBrickMovedToPosition([player.position.x, player.position.y], positions, id=player.index)

    requestPlayerPosition: (player) ->
        positions = ([position.x, position.y] for position in @mazeModel.positionsReachableByPlayer(player))
        @client.reportBackWhenBrickMovedToAnyOfPositions([player.position.x, player.position.y], positions, id=player.index)

    ready: ->
        # Fade maze
        setTimeout(() =>
            @updateMaze()
        , 1500)

        # Wait for start positions
        setTimeout(() =>
            @waitForStartPositions()
        , 2500)

    resetMaze: ->

        # Clear maze
        @clearMaze()
        @tileLayers[0].alpha = 1.0

        # Create random maze and reset players
        @mazeModel.createRandomMaze()

        # Reset game state
        @gameState = GameState.INITIAL_PLACEMENT
        @currentPlayer = @mazeModel.players[0]

        # Clear updating state
        @isUpdatingMaze = false

    nextPlayerTurn: ->

        # Find next player
        index = @currentPlayer.index

        while true
            index = (index + 1) % @mazeModel.players.length
            if @mazeModel.players[index].state != PlayerState.DISABLED
                @currentPlayer = @mazeModel.players[index]
                break

        for player in @mazeModel.players
            if player.state != PlayerState.DISABLED
                player.state = PlayerState.IDLE
        @currentPlayer.state = PlayerState.TURN

        # Update maze
        @updateMaze()

        # Start brick move reporter
        setTimeout(() =>
            @requestPlayerPosition(@currentPlayer)
        , 2000)

    clearMaze: ->
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                @tileLayers[@visibleLayer].setTile(x, y, transparentTileIndex)

        @drawMaze()

    updateMaze: ->

        # Check already updating maze
        if @isUpdatingMaze
            setTimeout(() =>
                @updateMaze()
            , 1500)
            return

        @isUpdatingMaze = true

        # Shift layer
        @visibleLayer = if @visibleLayer == 0 then 1 else 0

        # Draw maze
        @drawMaze()

        # Fade new layer
        destinationAlpha = if @visibleLayer == 0 then 0.0 else 1.0

        fadeMazeTween = @kiwiState.game.tweens.create(@tileLayers[1]);
        fadeMazeTween.to({ alpha: destinationAlpha }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true)

        # Clear updating state
        setTimeout(() =>
            @isUpdatingMaze = false
        , 1000)

    drawMaze: ->

        # Draw black/transparent tiles
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                tileIndex = if @mazeModel.isBorderAtCoordinate(x, y) then transparentTileIndex else blackTileIndex
                @tileLayers[@visibleLayer].setTile(x, y, tileIndex)
                #entry = @mazeModel.entryAtCoordinate(x, y)
                #if entry.tileIndex != 22
                    #@tileLayers[@visibleLayer].setTile(x, y, entry.tileIndex)

        if not @mazeModel.players?
            return

        # Draw player tiles
        drawOrder = (i for i in [0..@mazeModel.players.length - 1])
        drawOrder.splice(@currentPlayer.index, 1)
        drawOrder.push(@currentPlayer.index)

        for playerIndex in drawOrder
            player = @mazeModel.players[playerIndex]
            if player.state == PlayerState.DISABLED
                continue

            for position in @mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2)
                entry = @mazeModel.entryAtPosition(position)
                @tileLayers[@visibleLayer].setTile(position.x, position.y, entry.tileIndex + darkenTileOffset)

            for position in @mazeModel.positionsReachableFromPosition(player.position, player.reachDistance)
                entry = @mazeModel.entryAtPosition(position)
                @tileLayers[@visibleLayer].setTile(position.x, position.y, entry.tileIndex + @tileOffset(player, position))

    tileOffset: (player, position) ->
        switch @gameState
            when GameState.INITIAL_PLACEMENT
                if player.state == PlayerState.INITIAL_PLACEMENT
                    if player.position.equals(position) then 0 else darkenTileOffset
                else 0
            when GameState.PLAYING_GAME
                if @currentPlayer.index == player.index then 0 else darkenTileOffset
            else 0

    positionOnMap: (position) ->
        return @positionOnMap(position.x, position.y)

    positionOnMap: (x, y) ->
        return new Position(
            (@kiwiState.game.stage.width * x) / @mazeModel.width,
            (@kiwiState.game.stage.height * y) / @mazeModel.height)
