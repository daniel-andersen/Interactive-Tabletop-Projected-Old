class MazeInfo
    client = new Client()

    test: ->
        client.connect(this.initializeBoard)

    initializeBoard: ->
        client.initializeTiledBoard(32, 20)
