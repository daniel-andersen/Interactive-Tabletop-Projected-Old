class ClientLibrary
    socket = null

    action = "action"
    payload = "payload";

    constructor: (@port = 8080) ->

    connect: ->
        disconnect()
        socket = new WebSocket("http://localhost:" + port + "")

    disconnect: ->
        if socket
            socket.close()
            socket = null

    initializeTiledBoard(tileCountX, tileCountY, borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT") ->
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

    requestTiledObjectPosition(validLocations) ->
        message = {
            action: "requestTiledObjectPosition",
            payload: {
                "validLocations": [[location.x, location.y] for location in validLocations]
            }
        }