EXAMPLE2 = EXAMPLE2 or {}
EXAMPLE2.Game = new Kiwi.State("Game")

example2Game = null

EXAMPLE2.Game.preload = ->
    @addImage("corners", "assets/img/game/corners.png")
    @addImage("marker_next", "assets/img/game/marker_next.png")

EXAMPLE2.Game.create = ->
    Kiwi.State::create.call(this)

    example2Game = new Example2Game(this)
    example2Game.start()

EXAMPLE2.Game.shutDown = ->
    Kiwi.State::shutDown.call(this)
    example2Game.stop()

EXAMPLE2.Game.update = ->
    Kiwi.State::update.call(this)
    example2Game.update()



class Example2Game
    
    constructor: (@kiwiState) ->
        @client = new Client()

        @scaleAnimCounter = 0.0

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
        @next_marker.scale = 1.0 + (Math.cos(@scaleAnimCounter) * 0.1)

    setupUi: ->

        # Show canvas
        content = document.getElementById("content")
        content.style.visibility = "visible"

        # Corners (for tracking board)
        @corners = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.corners, 0, 0)
        @kiwiState.addChild(@corners)

        # Next marker
        @next_marker = new Kiwi.GameObjects.Sprite(@kiwiState, @kiwiState.textures.marker_next, 0, 0)
        @next_marker.visible = false
        @kiwiState.addChild(@next_marker)

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

        # Next
        @nextMarkerId = 0
        image1 = new Image()
        image1.onload = () => @client.initializeShapeMarkerWithImage(@nextMarkerId, image1, 0.001, 0.4, (action, payload) =>
            @startNewGame()
        )
        image1.src = "assets/tracking/marker_next.png"

    startNewGame: ->

        # Detect next marker
        @client.reportBackWhenMarkerFound(@wholeBoardAreaId, @nextMarkerId, undefined, undefined, (action, payload) =>

            # Start tracking marker continously
            @client.startTrackingMarker(@wholeBoardAreaId, @nextMarkerId, undefined, (action, payload) =>

                # Set position
                position = new Position(payload["marker"]["x"], payload["marker"]["y"])
                angle = payload["marker"]["angle"]

                @next_marker.x = (@kiwiState.game.stage.width * position.x) - (@next_marker.width / 2.0)
                @next_marker.y = (@kiwiState.game.stage.height * position.y) - (@next_marker.height / 2.0)
                @next_marker.rotation = angle * Math.PI / 180.0
                @next_marker.visible = true

                # Continue reporting marker positions
                return false
            )
        )
