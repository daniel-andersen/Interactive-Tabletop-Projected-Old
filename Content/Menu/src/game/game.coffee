MENU = MENU or {}
MENU.Game = new Kiwi.State("Game")

menuGame = null

MENU.Game.preload = ->
    @addImage("corners", "assets/img/game/corners.png")
    @addImage("wheel_background", "assets/img/game/wheel_background.png")
    @addImage("wheel_foreground", "assets/img/game/wheel_foreground.png")
    @addImage("wheel_marker", "assets/img/game/wheel_marker.png")

MENU.Game.create = ->
    Kiwi.State::create.call(this)

    menuGame = new MenuGame(this)
    menuGame.start()

MENU.Game.shutDown = ->
    Kiwi.State::shutDown.call(this)
    menuGame.stop()

MENU.Game.update = ->
    Kiwi.State::update.call(this)
    menuGame.update()



WheelState =
    GONE: 0
    POSITIONING: 1
    SELECTING: 2


class MenuGame

    constructor: (@kiwiState) ->
        @client = new Client()

    start: ->
        @setup()
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

    setup: ->
        @menuArUcoMarkerIndex = 50

        @selectionsCount = 8

        @markerRelaxationTime = 2.0
        @markerStableTime = 1.0
        @markerStableDistance = 0.02
        @markerStartAngle = undefined
        @markerHistory = []

        @wheelState = WheelState.GONE

        @wheelPosition = undefined

    setupUi: ->

        # Show canvas
        content = document.getElementById("content")
        content.style.visibility = "visible"

        # Corners (for tracking board)
        @corners = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.corners, 0, 0)
        @kiwiState.addChild(@corners)

        # Wheel background
        @wheelBackground = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.wheel_background, 0, 0)
        @wheelBackground.visible = false
        @kiwiState.addChild(@wheelBackground)

        # Wheel marker
        @wheelMarker = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.wheel_marker, 0, 0)
        @wheelMarker.visible = false
        @kiwiState.addChild(@wheelMarker)

        # Wheel foreground
        @wheelForeground = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.wheel_foreground, 0, 0)
        @wheelForeground.visible = false
        @kiwiState.addChild(@wheelForeground)

    initializeBoard: ->
        @client.initializeBoard(undefined, undefined, (action, payload) =>
            @initializeBoardAreas()
        )

    initializeBoardAreas: ->

        # Whole board area
        @wholeBoardAreaId = 0
        @client.initializeBoardArea(0.0, 0.0, 1.0, 1.0, @wholeBoardAreaId, (action, payload) =>
            @startNewGame()
        )

    startNewGame: ->
        setTimeout(() =>
            @findMarker()
        , 2000)

    findMarker: ->
        @client.requestArUcoMarkers(@wholeBoardAreaId, 6, undefined, (action, payload) =>
            @foundMarkers(payload["markers"])
            @findMarker()
        )

    foundMarkers: (markers) ->

        # Update history
        @updateMarkerHistory()

        # Check if marker found
        if markers.length == 0 then return

        marker = undefined
        for m in markers
            if m["markerId"] == @menuArUcoMarkerIndex
                marker = m

        if not marker? then return

        # Add marker to history
        @markerHistory.push({
            "timestamp": Util.currentTimeSeconds(),
            "marker": marker
        })

        # Update wheel
        @updateWheel(marker)

    updateWheel: (marker) ->

        # Update wheel according to state
        if @wheelState == WheelState.GONE
            @showWheel(marker)
            return

        if @wheelState == WheelState.POSITIONING
            @updateWheelPosition(marker)
            return

        # Update marker rotation
        @updateSelectedAngle(marker)

    showWheel: (marker) ->

        # Change state
        @wheelState = WheelState.POSITIONING

        # Position wheel
        @updateWheelPosition(marker)

        # Hide foreground and marker
        @wheelForeground.alpha = 0.0
        @wheelMarker.alpha = 0.0

        # Show wheel
        @toggleWheel(true)

    startSelecting: () ->

        # Change state
        @wheelState = WheelState.SELECTING

        # Fade in foreground
        Util.fadeInElement(@wheelForeground, 500, @kiwiState)
        Util.fadeInElement(@wheelMarker, 500, @kiwiState, 250)

    updateWheelPosition: (marker) ->

        @wheelPosition = @wheelPositionFromMarker(marker)
        @markerStartAngle = @wheelAngleFromMarker(marker)

        @wheelBackground.x = @wheelPosition[0] - (@wheelBackground.width / 2.0)
        @wheelBackground.y = @wheelPosition[1] - (@wheelBackground.height / 2.0)
        @wheelBackground.rotation = 0.0

        @wheelMarker.x = @wheelPosition[0] - (@wheelMarker.width / 2.0)
        @wheelMarker.y = @wheelPosition[1] - (@wheelMarker.height / 2.0)
        @wheelMarker.rotation = 0.0

        @wheelForeground.x = @wheelPosition[0] - (@wheelForeground.width / 2.0)
        @wheelForeground.y = @wheelPosition[1] - (@wheelForeground.height / 2.0)
        @wheelForeground.rotation = 0.0

        # Check if stabalized
        lastMarker = undefined
        for m in @markerHistory
            if m["timestamp"] < Util.currentTimeSeconds() - @markerStableTime
                lastMarker = m["marker"]

        if lastMarker?
            deltaPosition = [lastMarker["x"] - marker["x"], lastMarker["y"] - marker["y"]]
            moveDistance = Math.sqrt(deltaPosition[0]*deltaPosition[0] + deltaPosition[1]*deltaPosition[1])
            if moveDistance < @markerStableDistance
                @startSelecting()

    updateSelectedAngle: (marker) ->
        @wheelSelection = Math.round((Util.angleDifference(@wheelAngleFromMarker(marker), @markerStartAngle) / (Math.PI * 2.0)) * @selectionsCount) % @selectionsCount
        @wheelMarker.rotation = @wheelSelection * Math.PI * 2.0 / @selectionsCount
        console.log("Wheel selection: " + @wheelSelection)

    updateMarkerHistory: ->

        # Update history
        while @markerHistory.length > 0 and @markerHistory[0]["timestamp"] < Util.currentTimeSeconds() - @markerRelaxationTime
            @markerHistory.shift()

        # Remove wheel
        if @markerHistory.length == 0
            @toggleWheel(false)
            @wheelState = WheelState.GONE

    toggleWheel: (toggle) ->
        @wheelBackground.visible = toggle
        @wheelMarker.visible = toggle
        @wheelForeground.visible = toggle

    wheelPositionFromMarker: (marker) ->
        return [marker["x"] * @kiwiState.game.stage.width, marker["y"] * @kiwiState.game.stage.height]

    wheelAngleFromMarker: (marker) ->
        return marker["angle"] * Math.PI / 180.0
