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

    reset: (resolution = undefined) ->
        this.sendMessage("reset",
            if resolution? then "resolution": resolution else {}
        )

    resetReporters: ->
        this.sendMessage("resetReporters", {})

    resetReporter: (reporterId) ->
        this.sendMessage("resetReporter", {
            "id": reporterId
        })

    takeScreenshot: (filename = undefined) ->
        this.sendMessage("takeScreenshot",
            if filename? then "filename": filename else {}
        )

    initializeBoard: (borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
        this.sendMessage("initializeBoard", {
            "borderPctX": borderPctX,
            "borderPctY": borderPctY,
            "cornerMarker": cornerMarker
        })

    initializeBoardArea: (x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined) ->
        this.sendMessage("initializeBoardArea", Object.assign({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }, if areaId? then {"id": areaId} else {}))

    initializeTiledBoardArea: (tileCountX, tileCountY, x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined) ->
        this.sendMessage("initializeTiledBoardArea", Object.assign({
            "tileCountX": tileCountX,
            "tileCountY": tileCountY,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }, if areaId? then {"id": areaId} else {}))

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
        this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", Object.assign({
              "areaId": areaId,
              "validPositions": validPositions,
              "stableTime": stableTime
        }, if id? then {"id": id} else {}))

    reportBackWhenBrickMovedToAnyOfPositions: (areaId, initialPosition, validPositions, id = undefined, stableTime = 1.5) ->
        this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", Object.assign({
            "areaId": areaId,
            "initialPosition": initialPosition,
            "validPositions": validPositions,
            "stableTime": stableTime
        }, if id? then {"id": id} else {}))

    reportBackWhenBrickMovedToPosition: (areaId, position, validPositions, id = undefined, stableTime = 1.5) ->
        this.sendMessage("reportBackWhenBrickMovedToPosition", Object.assign({
            "areaId": areaId,
            "position": position,
            "validPositions": validPositions,
            "stableTime": stableTime
        }, if id? then {"id": id} else {}))

    initializeImageMarker: (markerId, image) ->
        @convertImageToDataURL(image, (base64Image) ->
            this.sendMessage("initializeImageMarker", {
                "markerId": markerId,
                "imageBase64": base64Image
            })
        )

    initializeShapeMarkerWithContour: (markerId, contour) ->
        this.sendMessage("initializeShapeMarker", {
            "id": markerId,
            "shape": contour
        })

    initializeShapeMarkerWithImage: (markerId, image) ->
        @convertImageToDataURL(image, (base64Image) ->
            this.sendMessage("initializeShapeMarker", {
                "id": markerId,
                "imageBase64": base64Image
            })
        )

    reportBackWhenMarkerFound: (areaId, markerId, id = undefined, stableTime = 1.5, sleepTime = 1.0) ->
        this.sendMessage("reportBackWhenMarkerFound", Object.assign({
            "areaId": areaId,
            "markerId": markerId,
            "stableTime": stableTime,
            "sleepTime": sleepTime
        }, if id? then {"id": id} else {}))

    requestMarkers: (areaId, markerId, stableTime = 1.5) ->
        this.sendMessage("requestMarkers", {
            "areaId": areaId,
            "markerId": markerId,
            "stableTime": stableTime
        })

    sendMessage: (action, payload) ->
        message = {
            action: action,
            payload: payload
        }
        this.socket.send(JSON.stringify(message))



    convertImageToDataURL: (image, callback) ->
        canvas = document.createElement("CANVAS")
        canvas.width = image.width
        canvas.height = image.height

        ctx = canvas.getContext("2d")
        ctx.drawImage(image, 0, 0)

        dataURL = canvas.toDataURL("image/png")

        callback(dataURL)

        canvas = null
