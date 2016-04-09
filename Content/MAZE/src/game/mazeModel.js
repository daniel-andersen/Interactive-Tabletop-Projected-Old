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
    this.tileIndex = tileIndex != null ? tileIndex : 6;
  }

  return MazeEntry;

})();

MazeModel = (function() {
  function MazeModel() {
    this.numberOfPlayers = 4;
    this.width = 32;
    this.height = 20;
    this.blackTileIndex = 5;
    this.transparentTileIndex = 6;
    this.wallTileIndex = 19;
    this.hallwayTileIndex = 7;
  }

  MazeModel.prototype.createRandomMaze = function() {
    var entry, i, ref, results, x, y;
    this.placePlayers();
    this.resetMaze();
    this.createMaze();
    results = [];
    for (y = i = 0, ref = this.height - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
      results.push((function() {
        var j, ref1, results1;
        results1 = [];
        for (x = j = 0, ref1 = this.width - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
          entry = this.entryAtCoordinate(x, y);
          if (entry.tileType === TileType.WALL || entry.tileType === TileType.BORDER) {
            entry.tileIndex = this.randomWallIndex();
          }
          if (entry.tileType === TileType.HALLWAY) {
            entry.tileIndex = this.randomHallwayIndex();
          }
          if (entry.tileType === TileType.EMPTY) {
            results1.push(entry.tileIndex = this.transparentTileIndex);
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
      var i, ref, results;
      results = [];
      for (y = i = 0, ref = this.height - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
        results.push((function() {
          var j, ref1, results1;
          results1 = [];
          for (x = j = 0, ref1 = this.width - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
            results1.push(new MazeEntry(this.defaultTileTypeAtCoordinate(x, y)));
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.placePlayers = function() {
    var _;
    this.players = (function() {
      var i, ref, results;
      results = [];
      for (_ = i = 1, ref = this.numberOfPlayers; 1 <= ref ? i <= ref : i >= ref; _ = 1 <= ref ? ++i : --i) {
        results.push(new Player());
      }
      return results;
    }).call(this);
    this.players[0].position = new Position(0, this.height / 2);
    this.players[1].position = new Position(this.width - 1, this.height / 2);
    this.players[2].position = new Position(this.width / 2, 0);
    return this.players[3].position = new Position(this.width / 2, this.height - 1);
  };

  MazeModel.prototype.createMaze = function() {
    var adjacentHallway, adjacentHallways, adjacentPosition, i, j, len, len1, margin, oppositePosition, player, position, randomIndex, ref, ref1, results;
    this.positionsToVisit = [];
    ref = this.players;
    for (i = 0, len = ref.length; i < len; i++) {
      player = ref[i];
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
      for (j = 0, len1 = ref1.length; j < len1; j++) {
        adjacentPosition = ref1[j];
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
    var adjacentPosition, i, len, ref, results;
    this.entryAtPosition(position).tileType = TileType.HALLWAY;
    ref = this.adjacentPositions(position);
    results = [];
    for (i = 0, len = ref.length; i < len; i++) {
      adjacentPosition = ref[i];
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

  MazeModel.prototype.adjacentHallwayPositions = function(position) {
    var p, positions;
    positions = this.adjacentPositions(position);
    return (function() {
      var i, len, ref, results;
      ref = this.adjacentPositions(position);
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        p = ref[i];
        if (this.entryAtPosition(p).tileType === TileType.HALLWAY) {
          results.push(p);
        }
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.isPositionValid = function(position, margin) {
    if (margin == null) {
      margin = 0;
    }
    return position.x >= margin && position.y >= margin && position.x < this.width - margin && position.y < this.height - margin;
  };

  MazeModel.prototype.positionsReachableByPlayer = function(player) {
    return this.positionsReachableFromPosition(player.position, player.reachDistance);
  };

  MazeModel.prototype.positionsReachableFromPosition = function(position, maxDistance) {
    var _, adjacentPosition, distance, distanceMap, i, len, positions, positionsToVisit, ref;
    distanceMap = (function() {
      var i, ref, results;
      results = [];
      for (_ = i = 1, ref = this.height; 1 <= ref ? i <= ref : i >= ref; _ = 1 <= ref ? ++i : --i) {
        results.push((function() {
          var j, ref1, results1;
          results1 = [];
          for (_ = j = 1, ref1 = this.width; 1 <= ref1 ? j <= ref1 : j >= ref1; _ = 1 <= ref1 ? ++j : --j) {
            results1.push(-1);
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    distanceMap[position.y][position.x] = 0;
    positions = [];
    positionsToVisit = [position];
    while (positionsToVisit.length > 0) {
      position = positionsToVisit.splice(0, 1)[0];
      distance = distanceMap[position.y][position.x];
      if (distance >= maxDistance) {
        continue;
      }
      positions.push(position);
      ref = this.adjacentHallwayPositions(position);
      for (i = 0, len = ref.length; i < len; i++) {
        adjacentPosition = ref[i];
        if (distanceMap[adjacentPosition.y][adjacentPosition.x] === -1) {
          distanceMap[adjacentPosition.y][adjacentPosition.x] = distance + 1;
          positionsToVisit.push(adjacentPosition);
        }
      }
    }
    return positions;
  };

  MazeModel.prototype.randomWallIndex = function() {
    return Util.randomInRange(this.wallTileIndex, this.wallTileIndex + 6);
  };

  MazeModel.prototype.randomHallwayIndex = function() {
    return Util.randomInRange(this.hallwayTileIndex, this.hallwayTileIndex + 6);
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
