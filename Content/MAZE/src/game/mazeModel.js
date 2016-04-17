var Direction, MazeEntry, MazeModel, MazeWall, WallType, blackTileIndex, darkenTileOffset, directionMovements, transparentTileIndex, wallTileStartIndex,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

WallType = {
  UP: 1,
  RIGHT: 2,
  DOWN: 4,
  LEFT: 8,
  ALL_SIDES: 15
};

Direction = {
  UP: 0,
  RIGHT: 1,
  DOWN: 2,
  LEFT: 3
};

directionMovements = [[0, -1], [1, 0], [0, 1], [-1, 0]];

blackTileIndex = 5;

transparentTileIndex = 6;

wallTileStartIndex = 7;

darkenTileOffset = 20;

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
    this.granularity = 2;
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
      var j, ref, results;
      results = [];
      for (y = j = 1, ref = this.height; 1 <= ref ? j <= ref : j >= ref; y = 1 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (x = k = 1, ref1 = this.width; 1 <= ref1 ? k <= ref1 : k >= ref1; x = 1 <= ref1 ? ++k : --k) {
            results1.push(new MazeEntry());
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    this.validPositionMap = (function() {
      var j, ref, results;
      results = [];
      for (y = j = 0, ref = this.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (x = k = 0, ref1 = this.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
            results1.push(this.isCoordinateValid(x, y));
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    this.validPositionMap[this.players[0].position.y][this.players[0].position.x - this.granularity] = false;
    this.validPositionMap[this.players[0].position.y][this.players[0].position.x + this.granularity] = false;
    this.validPositionMap[this.players[1].position.y - this.granularity][this.players[1].position.x] = false;
    this.validPositionMap[this.players[1].position.y + this.granularity][this.players[1].position.x] = false;
    this.validPositionMap[this.players[2].position.y][this.players[2].position.x - this.granularity] = false;
    this.validPositionMap[this.players[2].position.y][this.players[2].position.x + this.granularity] = false;
    this.validPositionMap[this.players[3].position.y - this.granularity][this.players[3].position.x] = false;
    return this.validPositionMap[this.players[3].position.y + this.granularity][this.players[3].position.x] = false;
  };

  MazeModel.prototype.placePlayers = function() {
    var i;
    this.players = (function() {
      var j, ref, results;
      results = [];
      for (i = j = 0, ref = this.numberOfPlayers - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
        results.push(new Player(i));
      }
      return results;
    }).call(this);
    this.players[0].position = new Position(this.width / 2, 0);
    this.players[1].position = new Position(this.width - 1, this.height / 2);
    this.players[2].position = new Position(this.width / 2, this.height - 1);
    return this.players[3].position = new Position(0, this.height / 2);
  };

  MazeModel.prototype.createMaze = function() {
    var downPosition, entry, j, leftPosition, position, randomIndex, ref, results, rightPosition, stop, upPosition, wall, x, y;
    this.wallsToVisit = [];
    position = this.positionWithGranularity(new Position(this.width / 2, this.height / 2));
    this.removeWalls(position, new Position(position.x + 1, position.y));
    this.addAdjacentWallsToVisitList(position);
    while (this.wallsToVisit.length > 0) {
      randomIndex = Util.randomInRange(0, this.wallsToVisit.length);
      wall = this.wallsToVisit.splice(randomIndex, 1)[0];
      if (this.wallMaskAtPosition(wall.position1) !== WallType.ALL_SIDES && this.wallMaskAtPosition(wall.position2) !== WallType.ALL_SIDES) {
        continue;
      }
      this.removeWalls(wall.position1, wall.position2);
      this.addAdjacentWallsToVisitList(wall.position2);
    }
    this.digWalls(this.players[0].position, Direction.DOWN, stop = WallType.ALL_SIDES);
    this.digWalls(this.players[1].position, Direction.LEFT, stop = WallType.ALL_SIDES);
    this.digWalls(this.players[2].position, Direction.UP, stop = WallType.ALL_SIDES);
    this.digWalls(this.players[3].position, Direction.RIGHT, stop = WallType.ALL_SIDES);
    results = [];
    for (y = j = 0, ref = this.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      results.push((function() {
        var k, ref1, ref2, ref3, ref4, ref5, results1;
        results1 = [];
        for (x = k = 0, ref1 = this.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
          position = new Position(x, y);
          entry = this.entryAtPosition(position);
          upPosition = new Position(x, y - 1);
          if (this.isPositionValid(upPosition) && (ref2 = WallType.DOWN, indexOf.call(this.entryAtPosition(upPosition).walls, ref2) < 0)) {
            entry.walls = entry.walls.filter(function(type) {
              return type !== WallType.UP;
            });
          }
          rightPosition = new Position(x + 1, y);
          if (this.isPositionValid(rightPosition) && (ref3 = WallType.LEFT, indexOf.call(this.entryAtPosition(rightPosition).walls, ref3) < 0)) {
            entry.walls = entry.walls.filter(function(type) {
              return type !== WallType.RIGHT;
            });
          }
          downPosition = new Position(x, y + 1);
          if (this.isPositionValid(downPosition) && (ref4 = WallType.UP, indexOf.call(this.entryAtPosition(downPosition).walls, ref4) < 0)) {
            entry.walls = entry.walls.filter(function(type) {
              return type !== WallType.DOWN;
            });
          }
          leftPosition = new Position(x - 1, y);
          if (this.isPositionValid(leftPosition) && (ref5 = WallType.RIGHT, indexOf.call(this.entryAtPosition(leftPosition).walls, ref5) < 0)) {
            results1.push(entry.walls = entry.walls.filter(function(type) {
              return type !== WallType.LEFT;
            }));
          } else {
            results1.push(void 0);
          }
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeModel.prototype.calculateTileIndices = function() {
    var entry, j, ref, results, x, y;
    results = [];
    for (y = j = 0, ref = this.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      results.push((function() {
        var k, ref1, results1;
        results1 = [];
        for (x = k = 0, ref1 = this.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
          entry = this.entryAtCoordinate(x, y);
          results1.push(entry.tileIndex = this.tileIndexAtCoordinate(x, y));
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeModel.prototype.removeWalls = function(position1, position2, granularity) {
    var entry, wallType;
    if (granularity == null) {
      granularity = this.granularity;
    }
    entry = this.entryAtPosition(position1);
    wallType = this.wallTypeOfAdjacentPositions(position1, position2, granularity);
    entry.walls = entry.walls.filter(function(type) {
      return type !== wallType;
    });
    entry = this.entryAtPosition(position2);
    wallType = this.wallTypeOfAdjacentPositions(position2, position1, granularity);
    return entry.walls = entry.walls.filter(function(type) {
      return type !== wallType;
    });
  };

  MazeModel.prototype.addAdjacentWallsToVisitList = function(position, granularity) {
    var adjacentPosition, j, len, ref, results;
    if (granularity == null) {
      granularity = this.granularity;
    }
    ref = this.adjacentPositions(position, granularity);
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      adjacentPosition = ref[j];
      results.push(this.wallsToVisit.push(new MazeWall(position, adjacentPosition)));
    }
    return results;
  };

  MazeModel.prototype.adjacentPositions = function(position, granularity) {
    var p, positions;
    if (granularity == null) {
      granularity = this.granularity;
    }
    positions = [];
    p = new Position(position.x - granularity, position.y);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    p = new Position(position.x + granularity, position.y);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    p = new Position(position.x, position.y - granularity);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    p = new Position(position.x, position.y + granularity);
    if (this.isPositionValid(p)) {
      positions.push(p);
    }
    return positions;
  };

  MazeModel.prototype.adjacentConnectedPositions = function(position, granularity) {
    var p;
    if (granularity == null) {
      granularity = this.granularity;
    }
    return (function() {
      var j, len, ref, results;
      ref = this.adjacentPositions(position, granularity);
      results = [];
      for (j = 0, len = ref.length; j < len; j++) {
        p = ref[j];
        if (this.arePositionsConnected(position, p, granularity)) {
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
    var _, adjacentPosition, distance, distanceMap, granularity, j, len, positions, positionsToVisit, ref;
    distanceMap = (function() {
      var j, ref, results;
      results = [];
      for (_ = j = 1, ref = this.height; 1 <= ref ? j <= ref : j >= ref; _ = 1 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (_ = k = 1, ref1 = this.width; 1 <= ref1 ? k <= ref1 : k >= ref1; _ = 1 <= ref1 ? ++k : --k) {
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
      ref = this.adjacentConnectedPositions(position, granularity = 1);
      for (j = 0, len = ref.length; j < len; j++) {
        adjacentPosition = ref[j];
        if (distanceMap[adjacentPosition.y][adjacentPosition.x] === -1) {
          distanceMap[adjacentPosition.y][adjacentPosition.x] = distance + 1;
          positionsToVisit.push(adjacentPosition);
        }
      }
    }
    return positions;
  };

  MazeModel.prototype.digWalls = function(position, direction, stop) {
    var entry, granularity, nextPosition;
    if (stop == null) {
      stop = WallType.ALL_SIDES;
    }
    entry = this.entryAtPosition(position);
    while (this.wallMaskAtPosition(position) !== WallType.ALL_SIDES) {
      nextPosition = this.positionInDirection(position, direction);
      if (!this.isPositionValid(nextPosition)) {
        return;
      }
      this.removeWalls(position, nextPosition, granularity = 1);
      position = nextPosition;
      entry = this.entryAtPosition(nextPosition);
    }
  };

  MazeModel.prototype.positionInDirection = function(position, direction) {
    return new Position(position.x + directionMovements[direction][0], position.y + directionMovements[direction][1]);
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

  MazeModel.prototype.arePositionsConnected = function(position1, position2, granularity) {
    var wallType;
    if (granularity == null) {
      granularity = this.granularity;
    }
    wallType = this.wallTypeOfAdjacentPositions(position1, position2, granularity);
    return indexOf.call(this.entryAtPosition(position1).walls, wallType) < 0;
  };

  MazeModel.prototype.wallTypeOfAdjacentPositions = function(position1, position2, granularity) {
    if (granularity == null) {
      granularity = this.granularity;
    }
    if (position1.y === position2.y) {
      if (position1.x === position2.x - granularity) {
        return WallType.RIGHT;
      }
      if (position1.x === position2.x + granularity) {
        return WallType.LEFT;
      }
    }
    if (position1.x === position2.x) {
      if (position1.y === position2.y - granularity) {
        return WallType.DOWN;
      }
      if (position1.y === position2.y + granularity) {
        return WallType.UP;
      }
    }
    return 0;
  };

  MazeModel.prototype.isCoordinateValid = function(x, y) {
    return !this.isBorderAtCoordinate(x, y);
  };

  MazeModel.prototype.isBorderAtCoordinate = function(x, y) {
    if (x <= 1 && y <= 1) {
      return true;
    }
    if (x >= this.width - 2 && y <= 1) {
      return true;
    }
    if (x <= 1 && y >= this.height - 2) {
      return true;
    }
    if (x >= this.width - 2 && y >= this.height - 2) {
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

  MazeModel.prototype.positionWithGranularity = function(position, granularity) {
    if (granularity == null) {
      granularity = this.granularity;
    }
    return new Position(position.x - (position.x % granularity), position.y - (position.y % granularity));
  };

  return MazeModel;

})();

//# sourceMappingURL=mazeModel.js.map
