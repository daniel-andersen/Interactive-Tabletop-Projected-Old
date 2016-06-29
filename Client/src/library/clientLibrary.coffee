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
        json = {}
        if resolution? then json["resolution"] = resolution
        this.sendMessage("reset", json)

    resetReporters: ->
        this.sendMessage("resetReporters", {})

    resetReporter: (reporterId) ->
        this.sendMessage("resetReporter", {
            "id": reporterId
        })

    takeScreenshot: (filename = undefined) ->
        json = {}
        if filename? then json["filename"] = filename
        this.sendMessage("takeScreenshot", json)

    initializeBoard: (borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
        this.sendMessage("initializeBoard", {
            "borderPctX": borderPctX,
            "borderPctY": borderPctY,
            "cornerMarker": cornerMarker
        })

    initializeBoardArea: (x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined) ->
        json = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        if areaId? then json["id"] = areaId
        this.sendMessage("initializeBoardArea", json)

    initializeTiledBoardArea: (tileCountX, tileCountY, x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined) ->
        json = {
            "tileCountX": tileCountX,
            "tileCountY": tileCountY,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        if areaId? then json["id"] = areaId
        this.sendMessage("initializeTiledBoardArea", json)

    removeBoardAreas: ->
        this.sendMessage("removeBoardAreas", {})

    removeBoardArea: (areaId) ->
        this.sendMessage("removeBoardArea", {
            "id": areaId
        })

    removeMarkers: ->
        this.sendMessage("removeMarkers", {})

    removeMarker: (markerId) ->
        this.sendMessage("removeMarker", {
            "id": markerId
        })

    requestTiledObjectPosition: (areaId, validPositions) ->
        this.sendMessage("requestBrickPosition", {
            "areaId": areaId,
            "validPositions": validPositions
        })

    reportBackWhenBrickFoundAtAnyOfPositions: (areaId, validPositions, id = undefined, stableTime = 1.5) ->
        json = {
              "areaId": areaId,
              "validPositions": validPositions,
              "stableTime": stableTime
        }
        if id? then json["id"] = id
        this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", json)

    reportBackWhenBrickMovedToAnyOfPositions: (areaId, initialPosition, validPositions, id = undefined, stableTime = 1.5) ->
        json = {
            "areaId": areaId,
            "initialPosition": initialPosition,
            "validPositions": validPositions,
            "stableTime": stableTime
        }
        if id? then json["id"] = id
        this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", json)

    reportBackWhenBrickMovedToPosition: (areaId, position, validPositions, id = undefined, stableTime = 1.5) ->
        json = {
            "areaId": areaId,
            "position": position,
            "validPositions": validPositions,
            "stableTime": stableTime
        }
        if id? then json["id"] = id
        this.sendMessage("reportBackWhenBrickMovedToPosition", json)

    initializeImageMarker: (markerId, image) ->
        @convertImageToDataURL(image, (base64Image) =>
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
        @convertImageToDataURL(image, (base64Image) =>
            this.sendMessage("initializeShapeMarker", {
                "id": markerId,
                "imageBase64": base64Image
            })
        )

    reportBackWhenMarkerFound: (areaId, markerId, id = undefined, stableTime = 1.5, sleepTime = 1.0) ->
        json = {
            "areaId": areaId,
            "markerId": markerId,
            "stableTime": stableTime,
            "sleepTime": sleepTime
        }
        if id? then json["id"] = id
        this.sendMessage("reportBackWhenMarkerFound", json)

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
        dataURL = dataURL.replace(/^data:image\/png;base64,/, "")

        callback(dataURL)

        canvas = null
