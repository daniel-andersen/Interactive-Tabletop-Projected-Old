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

    takeScreenshot: (filename = undefined) ->
        if filename != undefined
            this.sendMessage("takeScreenshot", {
                "filename": filename
            })
        else
            this.sendMessage("takeScreenshot", {})

    initializeBoard: (borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
        this.sendMessage("initializeBoard", {
            "borderPctX": borderPctX,
            "borderPctY": borderPctY,
            "cornerMarker": cornerMarker
        })

    initializeTiledBoardArea: (tileCountX, tileCountY, x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined) ->
        if areaId != undefined
            this.sendMessage("initializeTiledBoardArea", {
                "id": areaId,
                "tileCountX": tileCountX,
                "tileCountY": tileCountY,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })
        else
            this.sendMessage("initializeTiledBoardArea", {
                "tileCountX": tileCountX,
                "tileCountY": tileCountY,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })

    removeBoardAreas: ->
        this.sendMessage("removeBoardAreas", {})

    removeBoardArea: (areaId) ->
        this.sendMessage("removeBoardArea", {
            "id": areaId
        })

    requestTiledObjectPosition: (areaId, validPositions) ->
        this.sendMessage("requestBrickPosition", {
            "areaId": areaId,
            "validPositions": validPositions
        })

    reportBackWhenBrickFoundAtAnyOfPositions: (areaId, validPositions, id = undefined, stableTime = 1.5) ->
        if id != undefined
            this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
                "areaId": areaId,
                "validPositions": validPositions,
                "stableTime": stableTime,
                "id": id
            })
        else
            this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
                "areaId": areaId,
                "validPositions": validPositions,
                "stableTime": stableTime
            })

    reportBackWhenBrickMovedToAnyOfPositions: (areaId, initialPosition, validPositions, id = undefined, stableTime = 1.5) ->
        if id != undefined
            this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
                "areaId": areaId,
                "initialPosition": initialPosition,
                "validPositions": validPositions,
                "stableTime": stableTime,
                "id": id
            })
        else
            this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
                "areaId": areaId,
                "initialPosition": initialPosition,
                "validPositions": validPositions,
                "stableTime": stableTime
            })

    reportBackWhenBrickMovedToPosition: (areaId, position, validPositions, id = undefined, stableTime = 1.5) ->
        if id != undefined
            this.sendMessage("reportBackWhenBrickMovedToPosition", {
                "areaId": areaId,
                "position": position,
                "validPositions": validPositions,
                "stableTime": stableTime,
                "id": id
            })
        else
            this.sendMessage("reportBackWhenBrickMovedToPosition", {
                "areaId": areaId,
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
