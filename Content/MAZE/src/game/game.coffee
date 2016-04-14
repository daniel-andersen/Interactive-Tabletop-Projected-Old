MAZE = MAZE or {}
MAZE.Game = new Kiwi.State("Game")

tileLayers = []

mazeGame = null

MAZE.Game.preload = ->
    @addJSON("tilemap", "assets/maps/maze.json")
    @addSpriteSheet("tiles", "assets/img/tiles/board_tiles.png", 40, 40)
    @addImage("logo", "assets/img/menu/title.png")

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
    PLAYER_TURN: 2



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
        @client.reset()

    onMessage: (json) ->
        switch json["action"]
            when "reset" then @initializeBoard()
            when "initializeTiledBoard" then @ready()



    startNewGame: ->

        # Prepare game state
        @gameState = GameState.INITIALIZING
        @currentPlayerIndex = 0

        # Prepare map
        @visibleLayer = 0

        @tileLayers[0].alpha = 1.0
        @tileLayers[1].alpha = 0.0

        @resetMaze()

        # Fade logo
        setTimeout(() =>
            fadeLogoTween = @kiwiState.game.tweens.create(@logo);
            fadeLogoTween.to({ alpha: 1.0 }, 2000, Kiwi.Animations.Tweens.Easing.Linear.In, true)
        , 500)

    setupUi: ->

        # Setup logo
        @logo = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.logo, 0, 0)
        @logo.alpha = 0.0

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
        @kiwiState.addChild(@logo)

        # Setup debug log
        statusTextField = new Kiwi.HUD.Widget.TextField(@kiwiState.game, "", 100, 10)
        statusTextField.style.color = "#00ff00"
        statusTextField.style.fontSize = "14px"
        statusTextField.style.textShadow = "-1px -1px 5px black, 1px -1px 5px black, -1px 1px 5px black, 1px 1px 5px black"
        @client.debug_textField = statusTextField
        @kiwiState.game.huds.defaultHUD.addWidget(statusTextField)



    initializeBoard: ->
        @client.initializeTiledBoard(@mazeModel.width, @mazeModel.height)

    waitForStartPositions: ->
        for i in [0..@mazeModel.players.length - 1]
            positions = ([position.x, position.y] for position in @mazeModel.positionsReachableByPlayer(@mazeModel.players[i]))
            @client.reportBackWhenTileAtAnyOfPositions(positions, id=i)

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

        # Draw transparent maze
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                @tileLayers[@visibleLayer].setTile(x, y, transparentTileIndex)

        # Create random maze and reset players
        @mazeModel.createRandomMaze()

        # Place players mode
        @gameState = GameState.INITIAL_PLACEMENT

    updateMaze: ->

        # Shift layer
        @visibleLayer = if @visibleLayer == 0 then 1 else 0

        # Draw maze
        @drawMaze()

        # Fade new layer
        destinationAlpha = if @visibleLayer == 0 then 0.0 else 1.0

        fadeMazeTween = @kiwiState.game.tweens.create(@tileLayers[1]);
        fadeMazeTween.to({ alpha: destinationAlpha }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true)

    drawMaze: ->

        # Draw transparent tiles
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                @tileLayers[@visibleLayer].setTile(x, y, transparentTileIndex)
                #entry = @mazeModel.entryAtCoordinate(x, y)
                #if entry.tileIndex != 22
                    #@tileLayers[@visibleLayer].setTile(x, y, entry.tileIndex)

        # Draw player tiles
        drawOrder = (i for i in [0..@mazeModel.numberOfPlayers - 1])
        drawOrder.splice(@currentPlayerIndex, 1)
        drawOrder.push(@currentPlayerIndex)

        for playerIndex in drawOrder
            player = @mazeModel.players[playerIndex]

            for position in @mazeModel.positionsReachableByPlayer(player)
                entry = @mazeModel.entryAtPosition(position)
                @tileLayers[@visibleLayer].setTile(position.x, position.y, entry.tileIndex + @tileOffset(player, position))

    tileOffset: (player, position) ->
        switch @gameState
            when GameState.INITIAL_PLACEMENT
                if player.position.equals(position) then 0 else darkenTileOffset
            else 0
