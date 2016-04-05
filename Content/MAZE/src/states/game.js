var MAZE, maze, tileLayers;

MAZE = MAZE || {};

MAZE.Game = new Kiwi.State("Game");

tileLayers = [];

maze = null;

MAZE.Game.preload = function() {
  this.addJSON("tilemap", "assets/maps/sample.json");
  return this.addSpriteSheet("tiles", "assets/img/tiles/board_tiles.png", 40, 40);
};

MAZE.Game.create = function() {
  Kiwi.State.prototype.create.call(this);
  maze = new Maze(this);
  return maze.start();
};

MAZE.Game.shutDown = function() {
  Kiwi.State.prototype.shutDown.call(this);
  return maze.stop();
};

MAZE.Game.update = function() {
  return Kiwi.State.prototype.update.call(this);
};

//# sourceMappingURL=game.js.map
