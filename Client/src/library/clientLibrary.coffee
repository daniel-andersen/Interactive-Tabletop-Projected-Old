class Client

    constructor: (@port = 9001) ->
        @debug_textField = null
        @debug_log = []
        @socket = undefined

        @socketOpen = false

    connect: (onSocketOpen, onMessage) ->
        @disconnect()

        @socket = new WebSocket("ws://localhost:" + @port + "/")

        @socket.onopen = (event) =>
            onSocketOpen()

        @socket.onmessage = (event) =>
            json = JSON.parse(event.data)
            onMessage(json)

            if @debug_textField?
                @debug_log.splice(0, 0, JSON.stringify(json))
                @debug_textField.text = @debug_log[..5].join("<br/>")


    disconnect: ->
        if @socket?
            @socket.close()
            @socket = undefined

    enableDebug: () ->
        @sendMessage("enableDebug", {})

    reset: (resolution = undefined) ->
        json = {}
        if resolution? then json["resolution"] = resolution
        @sendMessage("reset", json)

    resetReporters: ->
        @sendMessage("resetReporters", {})

    resetReporter: (reporterId) ->
        @sendMessage("resetReporter", {
            "id": reporterId
        })

    takeScreenshot: (filename = undefined) ->
        json = {}
        if filename? then json["filename"] = filename
        @sendMessage("takeScreenshot", json)

    initializeBoard: (borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
        @sendMessage("initializeBoard", {
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
        @sendMessage("initializeBoardArea", json)

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
        @sendMessage("initializeTiledBoardArea", json)

    removeBoardAreas: ->
        @sendMessage("removeBoardAreas", {})

    removeBoardArea: (areaId) ->
        @sendMessage("removeBoardArea", {
            "id": areaId
        })

    removeMarkers: ->
        @sendMessage("removeMarkers", {})

    removeMarker: (markerId) ->
        @sendMessage("removeMarker", {
            "id": markerId
        })

    requestTiledObjectPosition: (areaId, validPositions) ->
        @sendMessage("requestBrickPosition", {
            "areaId": areaId,
            "validPositions": validPositions
        })

    reportBackWhenBrickFoundAtAnyOfPositions: (areaId, validPositions, id = undefined, stabilityLevel = undefined) ->
        json = {
              "areaId": areaId,
              "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", json)

    reportBackWhenBrickMovedToAnyOfPositions: (areaId, initialPosition, validPositions, id = undefined, stabilityLevel = undefined) ->
        json = {
            "areaId": areaId,
            "initialPosition": initialPosition,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickMovedToAnyOfPositions", json)

    reportBackWhenBrickMovedToPosition: (areaId, position, validPositions, id = undefined, stabilityLevel = undefined) ->
        json = {
            "areaId": areaId,
            "position": position,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickMovedToPosition", json)

    initializeImageMarker: (markerId, image, minMatches = undefined) ->
        @convertImageToDataURL(image, (base64Image) =>
            json = {
                "markerId": markerId,
                "imageBase64": base64Image
            }
            if minMatches? then json["minMatches"] = minMatches
            @sendMessage("initializeImageMarker", json)
        )

    initializeHaarClassifierMarker: (markerId, filename) ->
        @readFileBase64(filename, (base64Data) =>
            @sendMessage("initializeHaarClassifierMarker", {
                "markerId": markerId,
                "dataBase64": base64Data
            })
        )

    initializeShapeMarkerWithContour: (markerId, contour, minArea = undefined, maxArea = undefined) ->
        json = {
            "markerId": markerId,
            "shape": contour
        }
        if minArea? then json["minArea"] = minArea
        if maxArea? then json["maxArea"] = maxArea
        @sendMessage("initializeShapeMarker", json)

    initializeShapeMarkerWithImage: (markerId, image, minArea = undefined, maxArea = undefined) ->
        @convertImageToDataURL(image, (base64Image) =>
            json = {
                "markerId": markerId,
                "imageBase64": base64Image
            }
            if minArea? then json["minArea"] = minArea
            if maxArea? then json["maxArea"] = maxArea
            @sendMessage("initializeShapeMarker", json)
        )

    reportBackWhenMarkerFound: (areaId, markerId, id = undefined, stabilityLevel = undefined) ->
        json = {
            "areaId": areaId,
            "markerId": markerId
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenMarkerFound", json)

    requestMarkers: (areaId, markerIds, id = undefined, stabilityLevel = undefined) ->
        json = {
            "areaId": areaId,
            "markerIds": markerIds
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("requestMarkers", json)

    startTrackingMarker: (areaId, markerId, id = undefined) ->
        json = {
            "areaId": areaId,
            "markerId": markerId
        }
        if id? then json["id"] = id
        @sendMessage("startTrackingMarker", json)

    sendMessage: (action, payload) ->
        message = {
            "action": action,
            "payload": payload
        }
        @socket.send(JSON.stringify(message))



    convertImageToDataURL: (image, callback) ->
        canvas = document.createElement("CANVAS")
        canvas.width = image.width
        canvas.height = image.height

        ctx = canvas.getContext("2d")
        ctx.drawImage(image, 0, 0)

        dataURL = canvas.toDataURL("image/png")
        dataURL = dataURL.replace(/^.*;base64,/, "")

        callback(dataURL)

        canvas = null

    readFileBase64: (filename, callback) ->
        xhr = new XMLHttpRequest()
        xhr.open("GET", filename, true)
        xhr.responseType = "blob"

        xhr.onload = (e) ->
            if this.status == 200
                blob = new Blob([this.response], {type: "text/xml"})

                fileReader = new FileReader()
                fileReader.onload = (e) =>
                    contents = e.target.result
                    contents = contents.replace(/^.*;base64,/, "")
                    callback(contents)
                fileReader.onerror = (e) =>
                    console.log("Error loading file: " + e)

                fileReader.readAsDataURL(blob)

        xhr.send();
