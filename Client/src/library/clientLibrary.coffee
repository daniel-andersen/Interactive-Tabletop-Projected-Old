class Client
    socket = null

    action = "action"
    payload = "payload";

    constructor: (@port = 9001) ->
        @debug_textField = null
        @debug_log = []

        this.socketOpen = false

    connect: (onSocketOpen, onMessage) ->
        this.disconnect()

        this.socket = new WebSocket("ws://localhost:" + this.port + "/")

        this.socket.onopen = (event) =>
            onSocketOpen()

        this.socket.onmessage = (event) =>
            json = JSON.parse(event.data)
            onMessage(json)

            if @debug_textField?
                @debug_log.splice(0, 0, JSON.stringify(json))
                @debug_textField.text = @debug_log[..5].join("<br/>")


    disconnect: ->
        if this.socket
            this.socket.close()
            this.socket = null

    enableDebug: () ->
        this.sendMessage("enableDebug", {})

    reset: (resolution = null) ->
        if resolution?
            this.sendMessage("reset", {"resolution": resolution})
        else
            this.sendMessage("reset", {})

    resetReporters: ->
        this.sendMessage("resetReporters", {})

    resetReporter: (reporterId) ->
        this.sendMessage("resetReporter", {
            "id": reporterId
        })

    takeScreenshot: (filename = null) ->
        if filename != null
            this.sendMessage("takeScreenshot", {
                "filename": filename
            })
        else
            this.sendMessage("takeScreenshot", {})

    initializeTiledBoard: (tileCountX, tileCountY, borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
        this.sendMessage("initializeTiledBoard", {
            "tileCountX": tileCountX,
            "tileCountY": tileCountY,
            "borderPctX": borderPctX,
            "borderPctY": borderPctY,
            "cornerMarker": cornerMarker
        })

    requestTiledObjectPosition: (validPositions) ->
        this.sendMessage("requestBrickPosition", {
            "validPositions": validPositions
        })

    reportBackWhenBrickFoundAtAnyOfPositions: (validPositions, id = null, stableTime = 1.5) ->
        if id != null
            this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
                "validPositions": validPositions,
                "stableTime": stableTime,
                "id": id
            })
        else
            this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
                "validPositions": validPositions,
                "stableTime": stableTime
            })

    reportBackWhenBrickMovedToAnyOfPositions: (initialPosition, validPositions, id = null, stableTime = 1.5) ->
        if id != null
            this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
                "initialPosition": initialPosition,
                "validPositions": validPositions,
                "stableTime": stableTime,
                "id": id
            })
        else
            this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
                "initialPosition": initialPosition,
                "validPositions": validPositions,
                "stableTime": stableTime
            })

    reportBackWhenBrickMovedToPosition: (position, validPositions, id = null, stableTime = 1.5) ->
        if id != null
            this.sendMessage("reportBackWhenBrickMovedToPosition", {
                "position": position,
                "validPositions": validPositions,
                "stableTime": stableTime,
                "id": id
            })
        else
            this.sendMessage("reportBackWhenBrickMovedToPosition", {
                "position": position,
                "validPositions": validPositions,
                "stableTime": stableTime
            })

    sendMessage: (action, payload) ->
        message = {
            action: action,
            payload: payload
        }
        this.socket.send(JSON.stringify(message))
