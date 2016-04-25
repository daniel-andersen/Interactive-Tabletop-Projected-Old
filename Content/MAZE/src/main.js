var game, gameOptions;

gameOptions = {
  renderer: Kiwi.RENDERER_WEBGL,
  width: 1280,
  height: 800
};

game = new Kiwi.Game("content", "MAZE", null, gameOptions);

game.states.addState(MAZE.Game);

game.states.switchState("Game");

//# sourceMappingURL=main.js.map
