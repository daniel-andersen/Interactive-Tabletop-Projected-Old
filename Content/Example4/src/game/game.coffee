EXAMPLE4 = EXAMPLE4 or {}
EXAMPLE4.Game = new Kiwi.State("Game")

example4Game = null

EXAMPLE4.Game.preload = ->
    @addImage("corners", "assets/img/game/corners.png")
    @addImage("box", "assets/img/game/box.png")
    @addImage("marker_23", "assets/img/game/23.png")

EXAMPLE4.Game.create = ->
    Kiwi.State::create.call(this)

    example4Game = new Example4Game(this)
    example4Game.start()

EXAMPLE4.Game.shutDown = ->
    Kiwi.State::shutDown.call(this)
    example4Game.stop()

EXAMPLE4.Game.update = ->
    Kiwi.State::update.call(this)
    example4Game.update()



class Example4Game

    constructor: (@kiwiState) ->
        @client = new Client()

        @scaleAnimCounter = 0.0
        @aruco_marker_23 = undefined

    start: ->
        @setupUi()

        @client.connect(
          (() => @reset()),
          ((json) => @onMessage(json))
        )

    stop: ->
        @client.disconnect()

    reset: ->
        @client.reset([1600, 1200], (action, payload) =>
            @client.enableDebug()
            @initializeBoard()
        )

    onMessage: (json) ->

    update: ->
        @scaleAnimCounter += 0.1
        if @aruco_marker_23?
            @aruco_marker_23.scale = 1.0 + (Math.cos(@scaleAnimCounter) * 0.1)

    setupUi: ->

        # Show canvas
        content = document.getElementById("content")
        content.style.visibility = "visible"

        # Corners (for tracking board)
        @corners = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.corners, 0, 0)
        @kiwiState.addChild(@corners)

    initializeBoard: ->
        @client.initializeBoard(undefined, undefined, (action, payload) =>
            @initializeBoardAreas()
        )

    initializeBoardAreas: ->

        # Whole board
        @wholeBoardAreaId = 0
        @client.initializeBoardArea(0.0, 0.0, 1.0, 1.0, @wholeBoardAreaId, (action, payload) =>
            @initializeMarkers()
        )

    initializeMarkers: ->

        # ArUco marker with ID 23
        @arUcoMarkerId = 0
        @client.initializeArUcoMarker(@arUcoMarkerId, 23, 6, undefined, (action, payload) =>
            @startNewGame()
        )

    startNewGame: ->

        # Detect all ArUco markers
        @client.requestArUcoMarkers(@wholeBoardAreaId, 6, undefined, (action, payload) =>
            for marker in payload["markers"]
                box = new Kiwi.GameObjects.Sprite(@kiwiState, @kiwiState.textures.box, 0, 0)
                @kiwiState.addChild(box)

                position = new Position(marker["x"], marker["y"])
                angle = marker["angle"]

                box.x = (@kiwiState.game.stage.width * position.x) - (box.width / 2.0)
                box.y = (@kiwiState.game.stage.height * position.y) - (box.height / 2.0)
                box.rotation = angle * Math.PI / 180.0
        )

        # Detect ArUco marker with ID 23
        @client.reportBackWhenMarkerFound(@wholeBoardAreaId, @arUcoMarkerId, undefined, undefined, (action, payload) =>
            position = new Position(payload["marker"]["x"], payload["marker"]["y"])
            angle = payload["marker"]["angle"]

            @aruco_marker_23 = new Kiwi.GameObjects.Sprite(@kiwiState, @kiwiState.textures.marker_23, 0, 0)
            @kiwiState.addChild(@aruco_marker_23)

            @aruco_marker_23.x = (@kiwiState.game.stage.width * position.x) - (@aruco_marker_23.width / 2.0)
            @aruco_marker_23.y = (@kiwiState.game.stage.height * position.y) - (@aruco_marker_23.height / 2.0)
            @aruco_marker_23.rotation = angle * Math.PI / 180.0
        )
