class Client

    constructor: (@port = 9001) ->
        @debug_textField = null
        @debug_log = []
        @socket = undefined

        @socketOpen = false

        @requests = {}

    connect: (onSocketOpen, onMessage) ->
        @disconnect()

        @socket = new WebSocket("ws://localhost:" + @port + "/")

        @socket.onopen = (event) =>
            onSocketOpen()

        @socket.onmessage = (event) =>
            json = JSON.parse(event.data)
            @performCompletionCallbackForRequest(json)

            onMessage(json)

            if @debug_textField?
                @debug_log.splice(0, 0, JSON.stringify(json))
                @debug_textField.text = @debug_log[..5].join("<br/>")


    disconnect: ->
        if @socket?
            @socket.close()
            @socket = undefined

    enableDebug: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("enableDebug", {
            "requestId": requestId
        })

    reset: (resolution = undefined, completionCallback = undefined) ->
        @requests = {}
        requestId = @addCompletionCallback(completionCallback)
        json = {"requestId": requestId}
        if resolution? then json["resolution"] = resolution
        @sendMessage("reset", json)

    resetReporters: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("resetReporters", {
            "requestId": requestId
        })

    resetReporter: (reporterId, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("resetReporter", {
            "requestId": requestId,
            "id": reporterId
        })

    takeScreenshot: (filename = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {"requestId": requestId}
        if filename? then json["filename"] = filename
        @sendMessage("takeScreenshot", json)

    initializeBoard: (borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT", completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("initializeBoard", {
            "requestId": requestId,
            "borderPctX": borderPctX,
            "borderPctY": borderPctY,
            "cornerMarker": cornerMarker
        })

    initializeBoardArea: (x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        if areaId? then json["id"] = areaId
        @sendMessage("initializeBoardArea", json)

    initializeTiledBoardArea: (tileCountX, tileCountY, x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "tileCountX": tileCountX,
            "tileCountY": tileCountY,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        if areaId? then json["id"] = areaId
        @sendMessage("initializeTiledBoardArea", json)

    removeBoardAreas: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeBoardAreas", {
            "requestId": requestId
        })

    removeBoardArea: (areaId, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeBoardArea", {
            "requestId": requestId,
            "id": areaId
        })

    removeMarkers: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeMarkers", {
            "requestId": requestId
        })

    removeMarker: (markerId, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeMarker", {
            "requestId": requestId,
            "id": markerId
        })

    requestTiledObjectPosition: (areaId, validPositions, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("requestBrickPosition", {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        })

    reportBackWhenBrickFoundAtAnyOfPositions: (areaId, validPositions, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", json)

    reportBackWhenBrickMovedToAnyOfPositions: (areaId, initialPosition, validPositions, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "initialPosition": initialPosition,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickMovedToAnyOfPositions", json)

    reportBackWhenBrickMovedToPosition: (areaId, position, validPositions, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "position": position,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickMovedToPosition", json)

    initializeImageMarker: (markerId, image, minMatches = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @convertImageToDataURL(image, (base64Image) =>
            json = {
                "requestId": requestId,
                "markerId": markerId,
                "imageBase64": base64Image
            }
            if minMatches? then json["minMatches"] = minMatches
            @sendMessage("initializeImageMarker", json)
        )

    initializeHaarClassifierMarker: (markerId, filename, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @readFileBase64(filename, (base64Data) =>
            @sendMessage("initializeHaarClassifierMarker", {
                "requestId": requestId,
                "markerId": markerId,
                "dataBase64": base64Data
            })
        )

    initializeShapeMarkerWithContour: (markerId, contour, minArea = undefined, maxArea = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "markerId": markerId,
            "shape": contour
        }
        if minArea? then json["minArea"] = minArea
        if maxArea? then json["maxArea"] = maxArea
        @sendMessage("initializeShapeMarker", json)

    initializeShapeMarkerWithImage: (markerId, image, minArea = undefined, maxArea = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @convertImageToDataURL(image, (base64Image) =>
            json = {
                "requestId": requestId,
                "markerId": markerId,
                "imageBase64": base64Image
            }
            if minArea? then json["minArea"] = minArea
            if maxArea? then json["maxArea"] = maxArea
            @sendMessage("initializeShapeMarker", json)
        )

    reportBackWhenMarkerFound: (areaId, markerId, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "markerId": markerId
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenMarkerFound", json)

    requestMarkers: (areaId, markerIds, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "markerIds": markerIds
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("requestMarkers", json)

    startTrackingMarker: (areaId, markerId, id = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
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


    addCompletionCallback: (completionCallback) ->
        if completionCallback?
            requestId = ClientUtil.randomRequestId()
            @requests[requestId] = {"timestamp": Date.now(), "completionCallback": completionCallback}
            return requestId
        else
            return undefined

    performCompletionCallbackForRequest: (json) ->

        # Extract fields
        action = json["action"]
        requestId = json["requestId"]
        payload = json["payload"]

        # Json validation
        if not action? or not requestId? or not payload?
            return

        # Extract request from request dict
        requestDict = @requests[requestId]

        if not requestDict?
            return

        # Fire callback handler
        completionCallback = requestDict["completionCallback"]

        shouldRemoveRequest = completionCallback(action, payload)

        # Delete request if not explicitely specified otherwise by callback handler
        if not shouldRemoveRequest? or shouldRemoveRequest
            delete @requests[requestId]


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
