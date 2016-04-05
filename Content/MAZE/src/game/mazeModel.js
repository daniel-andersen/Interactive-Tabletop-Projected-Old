var MazeEntry, MazeModel, TileType;

TileType = {
  WALL: 0,
  HALLWAY: 1
};

MazeEntry = (function() {
  function MazeEntry(tileType) {
    this.tileType = tileType != null ? tileType : TileType.WALL;
  }

  return MazeEntry;

})();

MazeModel = (function() {
  function MazeModel() {
    var _;
    this.numberOfPlayers = 4;
    this.width = 32;
    this.height = 20;
    this.playerDefaultReachDistance = 4;
    this.playerReachDistance = [
      (function() {
        var i, ref, results;
        results = [];
        for (_ = i = 1, ref = this.numberOfPlayers; 1 <= ref ? i <= ref : i >= ref; _ = 1 <= ref ? ++i : --i) {
          results.push(this.playerDefaultReachDistance);
        }
        return results;
      }).call(this)
    ];
    this.granularity = 2;
    this.wallMinLength = 2;
    this.wallMaxLength = 3;
  }

  MazeModel.prototype.createRandomMaze = function() {
    return this.resetMaze();
  };

  MazeModel.prototype.resetMaze = function() {
    var x, y;
    return this.maze = [
      (function() {
        var i, ref, results;
        results = [];
        for (y = i = 0, ref = this.height - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
          results.push([
            (function() {
              var j, ref1, results1;
              results1 = [];
              for (x = j = 0, ref1 = this.width - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
                results1.push(new MazeEntry(this.isBorder(x, y) ? TileType.WALL : TileType.HALLWAY));
              }
              return results1;
            }).call(this)
          ]);
        }
        return results;
      }).call(this)
    ];
  };

  MazeModel.prototype.isBorder = function(x, y) {
    return x === 0 || y === 0 || x === this.width - 1 || y === this.height - 1;
  };

  return MazeModel;

})();

//# sourceMappingURL=mazeModel.js.map
