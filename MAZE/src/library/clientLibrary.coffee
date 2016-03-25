class Client
    socket = null

    action = "action"
    payload = "payload";

    constructor: (@port = 9001) ->
        this.socketOpen = false

    connect: (onSocketOpen) ->
        this.disconnect()
        this.socket = new WebSocket("ws://localhost:" + this.port + "/")

        this.socket.onopen = (event) =>
            onSocketOpen()

        this.socket.onmessage = (event) =>
            this.handleMessage(event.data)

    disconnect: ->
        if this.socket
            this.socket.close()
            this.socket = null

    handleMessage: (message) ->
        alert(message)

    initializeTiledBoard: (tileCountX, tileCountY, borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
        message = {
            action: "initializeTiledBoard",
            payload: {
                "tileCountX": tileCountX,
                "tileCountY": tileCountY,
                "borderPctX": borderPctX,
                "borderPctY": borderPctY,
                "cornerMarker": cornerMarker
            }
        }
        this.socket.send(JSON.stringify(message))

    requestTiledObjectPosition: (validLocations) ->
        message = {
            action: "requestTiledObjectPosition",
            payload: {
                "validLocations": [[location.x, location.y] for location in validLocations]
            }
        }