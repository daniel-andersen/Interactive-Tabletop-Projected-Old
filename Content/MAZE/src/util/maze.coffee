class Maze

    constructor: (@kiwiState) ->
        @client = new Client()

    start: ->
        @setupUi()
        @client.connect((() => @reset()), ((json) => @onMessage(json)))

    stop: ->
        @client.disconnect()

    reset: ->
        @client.reset()

    onMessage: (json) ->
        switch json["action"]
            when "reset" then @initializeBoard()
            when "initializeTiledBoard" then @ready()



    setupUi: ->
        @tilemap = new Kiwi.GameObjects.Tilemap.TileMap(@kiwiState, "tilemap", @kiwiState.textures.tiles)
        @logo = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.logo, 0, 0)
        @logo.alpha = 0.0

        borderLayer = @tilemap.getLayerByName("Border Layer")

        @tileLayers = []
        @tileLayers.push(@tilemap.getLayerByName("Tile Layer 1"))
        @tileLayers.push(@tilemap.getLayerByName("Tile Layer 2"))

        for tileLayer in @tileLayers
            tileLayer.alpha = 0.0

        @kiwiState.addChild(borderLayer)
        @kiwiState.addChild(@tileLayers[0])
        @kiwiState.addChild(@tileLayers[1])
        @kiwiState.addChild(@logo)

        statusTextField = new Kiwi.HUD.Widget.TextField(@kiwiState.game, "", 100, 10)
        statusTextField.style.color = "#00ff00"
        statusTextField.style.fontSize = "14px"
        statusTextField.style.textShadow = "-1px -1px 5px black, 1px -1px 5px black, -1px 1px 5px black, 1px 1px 5px black"
        @client.debug_textField = statusTextField
        @kiwiState.game.huds.defaultHUD.addWidget(statusTextField)

        # Fade logo
        setTimeout(() =>
            fadeLogoTween = @kiwiState.game.tweens.create(@logo);
            fadeLogoTween.to({ alpha: 1.0 }, 2000, Kiwi.Animations.Tweens.Easing.Linear.In, true)
        , 500)

        # Fade maze
        setTimeout(() =>
            fadeMazeTween = @kiwiState.game.tweens.create(@tileLayers[0]);
            fadeMazeTween.to({ alpha: 1.0 }, 2000, Kiwi.Animations.Tweens.Easing.Linear.In, true)
        , 2500)



    initializeBoard: ->
        @client.initializeTiledBoard(32, 20)

    waitForStartPositions: ->
        @client.reportBackWhenTileAtAnyOfPositions([[10, 10], [11, 10], [12, 10]])

    ready: ->
        console.log "Ready!"
        @waitForStartPositions()
