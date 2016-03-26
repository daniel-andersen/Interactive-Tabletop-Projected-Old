class MazeInfo
    client = new Client()

    test: ->
        client.connect (() => this.reset()), ((json) => this.onMessage(json))

    reset: ->
        client.reset()

    onMessage: (json) ->
        switch json["action"]
            when "reset" then this.initializeBoard()
            when "initializeTiledBoard" then this.start()

    initializeBoard: ->
        client.initializeTiledBoard(32, 20)

    start: ->
        console.log "Ready!"
