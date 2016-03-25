var MazeInfo;

MazeInfo = (function() {
  var client;

  function MazeInfo() {}

  client = new Client();

  MazeInfo.prototype.test = function() {
    return client.connect(this.initializeBoard);
  };

  MazeInfo.prototype.initializeBoard = function() {
    return client.initializeTiledBoard(32, 20);
  };

  return MazeInfo;

})();

//# sourceMappingURL=maze.js.map
