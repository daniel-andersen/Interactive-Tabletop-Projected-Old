var MazeInfo;

MazeInfo = (function() {
  var client;

  function MazeInfo() {}

  client = new Client();

  MazeInfo.prototype.test = function() {
    return client.connect(((function(_this) {
      return function() {
        return _this.reset();
      };
    })(this)), ((function(_this) {
      return function(json) {
        return _this.onMessage(json);
      };
    })(this)));
  };

  MazeInfo.prototype.reset = function() {
    return client.reset();
  };

  MazeInfo.prototype.onMessage = function(json) {
    switch (json["action"]) {
      case "reset":
        return this.initializeBoard();
      case "initializeTiledBoard":
        return this.start();
    }
  };

  MazeInfo.prototype.initializeBoard = function() {
    return client.initializeTiledBoard(32, 20);
  };

  MazeInfo.prototype.waitForStartPositions = function() {
    return client.reportBackWhenTileAtAnyOfPositions([[10, 10], [11, 10], [12, 10]]);
  };

  MazeInfo.prototype.start = function() {
    console.log("Ready!");
    return this.waitForStartPositions();
  };

  return MazeInfo;

})();

//# sourceMappingURL=maze.js.map
