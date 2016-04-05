class MazeInfo

    constructor: ->
        @client = new Client()

    startup: ->
        @client.connect (() => this.reset()), ((json) => this.onMessage(json))

    reset: ->
        @client.reset()

    onMessage: (json) ->
        switch json["action"]
            when "reset" then this.initializeBoard()
            when "initializeTiledBoard" then this.start()

    initializeBoard: ->
        @client.initializeTiledBoard(32, 20)

    waitForStartPositions: ->
        @client.reportBackWhenTileAtAnyOfPositions([[10, 10], [11, 10], [12, 10]])

    start: ->
        console.log "Ready!"
        this.waitForStartPositions()
