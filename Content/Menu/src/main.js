var game, gameOptions;

gameOptions = {
  renderer: Kiwi.RENDERER_WEBGL,
  deviceTarget: Kiwi.TARGET_BROWSER,
  width: 1280,
  height: 800
};

game = new Kiwi.Game("content", "MENU", null, gameOptions);

game.states.addState(MENU.Game);

game.states.switchState("Game");

//# sourceMappingURL=main.js.map
