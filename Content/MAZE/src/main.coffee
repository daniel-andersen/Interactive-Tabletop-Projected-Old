gameOptions =
  renderer: Kiwi.RENDERER_CANVAS
  width: 1280
  height: 800

game = new Kiwi.Game("content", "MAZE", null, gameOptions)
game.states.addState(MAZE.Game)
game.states.switchState("Game")
