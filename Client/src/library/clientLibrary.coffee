class Client
    socket = null

    action = "action"
    payload = "payload";

    constructor: (@port = 9001) ->
        this.socketOpen = false

    connect: (onSocketOpen, onMessage) ->
        this.disconnect()
        this.socket = new WebSocket("ws://localhost:" + this.port + "/")

        this.socket.onopen = (event) =>
            onSocketOpen()

        this.socket.onmessage = (event) =>
            json = JSON.parse(event.data)
            onMessage(json)

    disconnect: ->
        if this.socket
            this.socket.close()
            this.socket = null

    reset: () ->
        message = {
            action: "reset",
            payload: {}
        }
        this.socket.send(JSON.stringify(message))

    initializeTiledBoard: (tileCountX, tileCountY, borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
        this.sendMessage("initializeTiledBoard", {
            "tileCountX": tileCountX,
            "tileCountY": tileCountY,
            "borderPctX": borderPctX,
            "borderPctY": borderPctY,
            "cornerMarker": cornerMarker
        })

    requestTiledObjectPosition: (validLocations) ->
        this.sendMessage("requestTiledObjectPosition", {
            "validLocations": validLocations
        })

    reportBackWhenTileAtAnyOfPositions: (validLocations) ->
        this.sendMessage("reportBackWhenTileAtAnyOfPositions", {
            "validLocations": validLocations
        })

    sendMessage: (action, payload) ->
        message = {
            action: action,
            payload: payload
        }
        this.socket.send(JSON.stringify(message))
