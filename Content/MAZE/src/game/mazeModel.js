var Direction, MazeEntry, MazeModel, TileType;

Direction = {
  UP: 0,
  RIGHT: 1,
  DOWN: 2,
  LEFT: 3
};

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
    var i;
    this.numberOfPlayers = 4;
    this.players = (function() {
      var j, ref, results;
      results = [];
      for (i = j = 1, ref = this.numberOfPlayers; 1 <= ref ? j <= ref : j >= ref; i = 1 <= ref ? ++j : --j) {
        results.push(new Player());
      }
      return results;
    }).call(this);
    this.width = 32;
    this.height = 20;
    this.granularity = 2;
    this.wallMinLength = 2;
    this.wallMaxLength = 3;
  }

  MazeModel.prototype.createRandomMaze = function() {
    var _, j;
    for (_ = j = 1; j <= 10; _ = ++j) {
      this.resetMaze();
      this.placePlayers();
      this.createWalls();
      return;
    }
  };

  MazeModel.prototype.resetMaze = function() {
    var x, y;
    return this.maze = (function() {
      var j, ref, results;
      results = [];
      for (y = j = 0, ref = this.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (x = k = 0, ref1 = this.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
            results1.push(new MazeEntry(this.isBorder(x, y) ? TileType.WALL : TileType.HALLWAY));
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.placePlayers = function() {
    this.players[0].position = new Position(0, this.height / 2);
    this.players[1].position = new Position(this.width - 1, this.height / 2);
    this.players[2].position = new Position(this.width / 2, 0);
    return this.players[3].position = new Position(this.width / 2, this.height - 1);
  };

  MazeModel.prototype.createWalls = function() {
    var i, j, k, len, numberOfWalls, player, ref, ref1, results;
    numberOfWalls = (this.width * 2 / 3) * this.height;
    for (i = j = 1, ref = numberOfWalls; 1 <= ref ? j <= ref : j >= ref; i = 1 <= ref ? ++j : --j) {
      this.attemptWallStart();
    }
    ref1 = this.players;
    results = [];
    for (k = 0, len = ref1.length; k < len; k++) {
      player = ref1[k];
      alert(player.position.y);
      results.push(this.entryAtPosition(player.position).tileType = TileType.HALLWAY);
    }
    return results;
  };

  MazeModel.prototype.attemptWallStart = function() {
    return this.attemptWallStartAtPosition(this.randomWallStart());
  };

  MazeModel.prototype.attemptWallStartAtPosition = function(position) {
    var direction, entry, length;
    entry = this.entryAtPosition(position);
    if (entry.tileType === TileType.WALL) {
      return;
    }
    direction = Util.randomInRange(0, 4);
    length = (Util.randomInRange(this.wallMinLength, this.wallMaxLength + 1) * this.granularity) + 1;
    return this.createWall(position, direction, length);
  };

  MazeModel.prototype.createWall = function(position, direction, length) {
    var entry, i, j, ref, stepX, stepY;
    stepX = direction === Direction.LEFT ? -1 : (direction === Direction.RIGHT ? 1 : 0);
    stepY = direction === Direction.UP ? -1 : (direction === Direction.DOWN ? 1 : 0);
    for (i = j = 1, ref = length; 1 <= ref ? j <= ref : j >= ref; i = 1 <= ref ? ++j : --j) {
      entry = this.entryAtPosition(position);
      if (entry.tileType === TileType.WALL) {
        return;
      }
      entry.tileType = TileType.WALL;
      position.x += stepX;
      position.y += stepY;
    }
  };

  MazeModel.prototype.randomWallStart = function() {
    return new Position(Util.randomInRange(0, this.width), Util.randomInRange(0, this.height));
  };

  MazeModel.prototype.entryAtPosition = function(position) {
    return this.maze[position.y][position.x];
  };

  MazeModel.prototype.isBorder = function(x, y) {
    return x === 0 || y === 0 || x === this.width - 1 || y === this.height - 1;
  };

  return MazeModel;

})();

//# sourceMappingURL=mazeModel.js.map
