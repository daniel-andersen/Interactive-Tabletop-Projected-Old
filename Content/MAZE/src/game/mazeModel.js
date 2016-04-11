var MazeEntry, MazeModel, MazeWall, WallType, blackTileIndex, transparentTileIndex, wallTileStartIndex,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

WallType = {
  UP: 1,
  RIGHT: 2,
  DOWN: 4,
  LEFT: 8,
  ALL_SIDES: 15,
  BORDER: 16
};

blackTileIndex = 5;

transparentTileIndex = 6;

wallTileStartIndex = 7;

MazeEntry = (function() {
  function MazeEntry(walls, tileIndex) {
    this.walls = walls != null ? walls : [WallType.UP, WallType.RIGHT, WallType.DOWN, WallType.LEFT];
    this.tileIndex = tileIndex != null ? tileIndex : transparentTileIndex;
  }

  return MazeEntry;

})();

MazeWall = (function() {
  function MazeWall(position11, position21) {
    this.position1 = position11;
    this.position2 = position21;
  }

  return MazeWall;

})();

MazeModel = (function() {
  function MazeModel() {
    this.numberOfPlayers = 4;
    this.width = 32;
    this.height = 20;
  }

  MazeModel.prototype.createRandomMaze = function() {
    this.placePlayers();
    this.resetMaze();
    this.createMaze();
    return this.calculateTileIndices();
  };

  MazeModel.prototype.resetMaze = function() {
    var x, y;
    this.maze = (function() {
      var i, ref, results;
      results = [];
      for (y = i = 1, ref = this.height; 1 <= ref ? i <= ref : i >= ref; y = 1 <= ref ? ++i : --i) {
        results.push((function() {
          var j, ref1, results1;
          results1 = [];
          for (x = j = 1, ref1 = this.width; 1 <= ref1 ? j <= ref1 : j >= ref1; x = 1 <= ref1 ? ++j : --j) {
            results1.push(new MazeEntry());
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    return this.validPositionMap = (function() {
      var i, ref, results;
      results = [];
      for (y = i = 0, ref = this.height - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
        results.push((function() {
          var j, ref1, results1;
          results1 = [];
          for (x = j = 0, ref1 = this.width - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
            results1.push(this.isCoordinateValid(x, y));
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
    this.players[0].position = new Position(this.width / 2, 0);
    this.players[1].position = new Position(this.width - 1, this.height / 2);
    this.players[2].position = new Position(this.width / 2, this.height - 1);
    return this.players[3].position = new Position(0, this.height / 2);
  };

  MazeModel.prototype.createMaze = function() {
    var adjacentPosition, randomIndex, results, wall;
    this.wallsToVisit = [];
    adjacentPosition = new Position(this.players[0].position.x, this.players[0].position.y + 1);
    this.removeWalls(this.players[0].position, adjacentPosition);
    this.addAdjacentWallsToVisitList(adjacentPosition);
    adjacentPosition = new Position(this.players[1].position.x - 1, this.players[1].position.y);
    this.removeWalls(this.players[1].position, adjacentPosition);
    this.addAdjacentWallsToVisitList(adjacentPosition);
    adjacentPosition = new Position(this.players[2].position.x, this.players[2].position.y - 1);
    this.removeWalls(this.players[2].position, adjacentPosition);
    this.addAdjacentWallsToVisitList(adjacentPosition);
    adjacentPosition = new Position(this.players[3].position.x + 1, this.players[3].position.y);
    this.removeWalls(this.players[3].position, adjacentPosition);
    this.addAdjacentWallsToVisitList(adjacentPosition);
    results = [];
    while (this.wallsToVisit.length > 0) {
      randomIndex = Util.randomInRange(0, this.wallsToVisit.length);
      wall = this.wallsToVisit.splice(randomIndex, 1)[0];
      if (this.wallMaskAtPosition(wall.position1) !== WallType.ALL_SIDES && this.wallMaskAtPosition(wall.position2) !== WallType.ALL_SIDES) {
        continue;
      }
      this.removeWalls(wall.position1, wall.position2);
      results.push(this.addAdjacentWallsToVisitList(wall.position2));
    }
    return results;
  };

  MazeModel.prototype.calculateTileIndices = function() {
    var entry, i, ref, results, x, y;
    results = [];
    for (y = i = 0, ref = this.height - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
      results.push((function() {
        var j, ref1, results1;
        results1 = [];
        for (x = j = 0, ref1 = this.width - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
          entry = this.entryAtCoordinate(x, y);
          results1.push(entry.tileIndex = this.tileIndexAtCoordinate(x, y));
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeModel.prototype.removeWalls = function(position1, position2) {
    var entry, wallType;
    entry = this.entryAtPosition(position1);
    wallType = this.wallTypeOfAdjacentPositions(position1, position2);
    entry.walls = entry.walls.filter(function(type) {
      return type !== wallType;
    });
    entry = this.entryAtPosition(position2);
    wallType = this.wallTypeOfAdjacentPositions(position2, position1);
    return entry.walls = entry.walls.filter(function(type) {
      return type !== wallType;
    });
  };

  MazeModel.prototype.addAdjacentWallsToVisitList = function(position) {
    var adjacentPosition, i, len, ref, results;
    ref = this.adjacentPositions(position);
    results = [];
    for (i = 0, len = ref.length; i < len; i++) {
      adjacentPosition = ref[i];
      results.push(this.wallsToVisit.push(new MazeWall(position, adjacentPosition)));
    }
    return results;
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

  MazeModel.prototype.adjacentConnectedPositions = function(position) {
    var p;
    return (function() {
      var i, len, ref, results;
      ref = this.adjacentPositions(position);
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        p = ref[i];
        if (this.arePositionsConnected(position, p)) {
          results.push(p);
        }
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.isPositionValid = function(position) {
    if (position.x < 0 || position.y < 0 || position.x > this.width - 1 || position.y > this.height - 1) {
      return false;
    }
    return this.validPositionMap[position.y][position.x];
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
      ref = this.adjacentConnectedPositions(position);
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

  MazeModel.prototype.wallMaskAtPosition = function(position) {
    return this.entryAtPosition(position).walls.reduce((function(t, s) {
      return t + s;
    }), 0);
  };

  MazeModel.prototype.entryAtCoordinate = function(x, y) {
    return this.maze[y][x];
  };

  MazeModel.prototype.entryAtPosition = function(position) {
    return this.maze[position.y][position.x];
  };

  MazeModel.prototype.arePositionsConnected = function(position1, position2) {
    var wallType;
    wallType = this.wallTypeOfAdjacentPositions(position1, position2);
    return indexOf.call(this.entryAtPosition(position1).walls, wallType) < 0;
  };

  MazeModel.prototype.wallTypeOfAdjacentPositions = function(position1, position2) {
    if (position1.y === position2.y) {
      if (position1.x === position2.x - 1) {
        return WallType.RIGHT;
      }
      if (position1.x === position2.x + 1) {
        return WallType.LEFT;
      }
    }
    if (position1.x === position2.x) {
      if (position1.y === position2.y - 1) {
        return WallType.DOWN;
      }
      if (position1.y === position2.y + 1) {
        return WallType.UP;
      }
    }
    return 0;
  };

  MazeModel.prototype.isCoordinateValid = function(x, y) {
    return !this.isBorderAtCoordinate(x, y);
  };

  MazeModel.prototype.isBorderAtCoordinate = function(x, y) {
    if (x <= 0 || y <= 0 || x >= this.width - 1 || y >= this.height - 1) {
      return true;
    }
    if (x === 1 && y === 1) {
      return true;
    }
    if (x === this.width - 2 && y === 1) {
      return true;
    }
    if (x === 1 && y === this.height - 2) {
      return true;
    }
    if (x === this.width - 2 && y === this.height - 2) {
      return true;
    }
    return false;
  };

  MazeModel.prototype.tileIndexAtCoordinate = function(x, y) {
    var entry;
    entry = this.entryAtCoordinate(x, y);
    return wallTileStartIndex + entry.walls.reduce((function(t, s) {
      return t + s;
    }), 0);
  };

  return MazeModel;

})();

//# sourceMappingURL=mazeModel.js.map
