var Direction, MazeEntry, MazeModel, TileType;

Direction = {
  UP: 0,
  RIGHT: 1,
  DOWN: 2,
  LEFT: 3
};

TileType = {
  WALL: 0,
  HALLWAY: 1,
  BORDER: 2,
  EMPTY: 3
};

MazeEntry = (function() {
  function MazeEntry(tileType, tileIndex) {
    this.tileType = tileType != null ? tileType : TileType.WALL;
    this.tileIndex = tileIndex != null ? tileIndex : 18;
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
  }

  MazeModel.prototype.createRandomMaze = function() {
    var entry, j, ref, results, x, y;
    this.placePlayers();
    this.resetMaze();
    this.createMaze();
    results = [];
    for (y = j = 0, ref = this.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      results.push((function() {
        var k, ref1, results1;
        results1 = [];
        for (x = k = 0, ref1 = this.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
          entry = this.entryAtCoordinate(x, y);
          if (entry.tileType === TileType.WALL || entry.tileType === TileType.BORDER) {
            entry.tileIndex = this.randomWallIndex();
          }
          if (entry.tileType === TileType.HALLWAY) {
            entry.tileIndex = this.randomHallwayIndex();
          }
          if (entry.tileType === TileType.EMPTY) {
            results1.push(entry.tileIndex = 18);
          } else {
            results1.push(void 0);
          }
        }
        return results1;
      }).call(this));
    }
    return results;
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
            results1.push(new MazeEntry(this.defaultTileTypeAtCoordinate(x, y)));
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

  MazeModel.prototype.createMaze = function() {
    var adjacentHallway, adjacentHallways, adjacentPosition, j, k, len, len1, margin, oppositePosition, player, position, randomIndex, ref, ref1, results;
    this.positionsToVisit = [];
    ref = this.players;
    for (j = 0, len = ref.length; j < len; j++) {
      player = ref[j];
      this.addHallwayAtPosition(player.position);
    }
    results = [];
    while (this.positionsToVisit.length > 0) {
      randomIndex = Util.randomInRange(0, this.positionsToVisit.length);
      position = this.positionsToVisit.splice(randomIndex, 1)[0];
      if (this.entryAtPosition(position).tileType === TileType.hallways) {
        continue;
      }
      adjacentHallways = [];
      ref1 = this.adjacentPositions(position);
      for (k = 0, len1 = ref1.length; k < len1; k++) {
        adjacentPosition = ref1[k];
        if (this.entryAtPosition(adjacentPosition).tileType === TileType.HALLWAY) {
          adjacentHallways.push(adjacentPosition);
        }
      }
      if (adjacentHallways.length !== 1) {
        continue;
      }
      adjacentHallway = adjacentHallways[0];
      oppositePosition = new Position(position.x - (adjacentHallway.x - position.x), position.y - (adjacentHallway.y - position.y));
      if (this.entryAtPosition(position).tileType !== TileType.WALL || this.entryAtPosition(position).tileType !== TileType.WALL) {
        continue;
      }
      if (!this.isPositionValid(oppositePosition, margin = 1)) {
        continue;
      }
      this.entryAtPosition(position).tileType = TileType.HALLWAY;
      results.push(this.addHallwayAtPosition(oppositePosition));
    }
    return results;
  };

  MazeModel.prototype.addHallwayAtPosition = function(position) {
    var adjacentPosition, j, len, ref, results;
    this.entryAtPosition(position).tileType = TileType.HALLWAY;
    ref = this.adjacentPositions(position);
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      adjacentPosition = ref[j];
      results.push(this.addPositionToVisitList(adjacentPosition));
    }
    return results;
  };

  MazeModel.prototype.addPositionToVisitList = function(position) {
    if (this.isPositionValid(position) && this.entryAtPosition(position).tileType === TileType.WALL) {
      return this.positionsToVisit.push(position);
    }
  };

  MazeModel.prototype.adjacentPositions = function(position) {
    var p, positions;
    positions = [];
    p = new Position(position.x - 1, position.y);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    p = new Position(position.x + 1, position.y);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    p = new Position(position.x, position.y - 1);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    p = new Position(position.x, position.y + 1);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    return positions;
  };

  MazeModel.prototype.isPositionValid = function(position, margin) {
    if (margin == null) {
      margin = 0;
    }
    return position.x >= margin && position.y >= margin && position.x < this.width - margin && position.y < this.height - margin;
  };

  MazeModel.prototype.randomWallIndex = function() {
    return Util.randomInRange(11, 17);
  };

  MazeModel.prototype.randomHallwayIndex = function() {
    return Util.randomInRange(5, 11);
  };

  MazeModel.prototype.entryAtCoordinate = function(x, y) {
    return this.maze[y][x];
  };

  MazeModel.prototype.entryAtPosition = function(position) {
    return this.maze[position.y][position.x];
  };

  MazeModel.prototype.defaultTileTypeAtCoordinate = function(x, y) {
    if ((x === 0 && y === 0) || (x === 1 && y === 0) || (x === 0 && y === 1)) {
      return TileType.EMPTY;
    }
    if ((x === 0 && y === this.height - 1) || (x === 1 && y === this.height - 1) || (x === 0 && y === this.height - 2)) {
      return TileType.EMPTY;
    }
    if ((x === this.width - 1 && y === 0) || (x === this.width - 2 && y === 0) || (x === this.width - 1 && y === 1)) {
      return TileType.EMPTY;
    }
    if ((x === this.width - 1 && y === this.height - 1) || (x === this.width - 2 && y === this.height - 1) || (x === this.width - 1 && y === this.height - 2)) {
      return TileType.EMPTY;
    }
    if (x === 0 || y === 0 || x === this.width - 1 || y === this.height - 1) {
      return TileType.BORDER;
    }
    if (x === 1 && y === 1) {
      return TileType.BORDER;
    }
    if (x === this.width - 2 && y === 1) {
      return TileType.BORDER;
    }
    if (x === 1 && y === this.height - 2) {
      return TileType.BORDER;
    }
    if (x === this.width - 2 && y === this.height - 2) {
      return TileType.BORDER;
    }
    return TileType.WALL;
  };

  MazeModel.prototype.isBorder = function(x, y) {
    return x === 0 || y === 0 || x === this.width - 1 || y === this.height - 1;
  };

  return MazeModel;

})();

//# sourceMappingURL=mazeModel.js.map
