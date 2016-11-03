gameOptions =
    renderer: Kiwi.RENDERER_WEBGL
    deviceTarget : Kiwi.TARGET_BROWSER
    width: 1280
    height: 800

game = new Kiwi.Game("content", "GEOMETRY", null, gameOptions)
game.states.addState(GEOMETRY.Game)
game.states.switchState("Game")
