var GameState, MAZE, MazeGame, mazeGame, tileLayers;

MAZE = MAZE || {};

MAZE.Game = new Kiwi.State("Game");

tileLayers = [];

mazeGame = null;

MAZE.Game.preload = function() {
  this.addJSON("tilemap", "assets/maps/maze.json");
  this.addSpriteSheet("tiles", "assets/img/tiles/board_tiles.png", 40, 40);
  this.addImage("logo", "assets/img/menu/title.png");
  return this.addImage("treasure", "assets/img/tiles/treasure.png");
};

MAZE.Game.create = function() {
  Kiwi.State.prototype.create.call(this);
  mazeGame = new MazeGame(this);
  return mazeGame.start();
};

MAZE.Game.shutDown = function() {
  Kiwi.State.prototype.shutDown.call(this);
  return mazeGame.stop();
};

MAZE.Game.update = function() {
  return Kiwi.State.prototype.update.call(this);
};

GameState = {
  INITIALIZING: 0,
  INITIAL_PLACEMENT: 1,
  PLAYING_GAME: 2
};

MazeGame = (function() {
  function MazeGame(kiwiState) {
    this.kiwiState = kiwiState;
    this.client = new Client();
    this.mazeModel = new MazeModel();
  }

  MazeGame.prototype.start = function() {
    this.setupUi();
    this.startNewGame();
    return this.client.connect(((function(_this) {
      return function() {
        return _this.reset();
      };
    })(this)), ((function(_this) {
      return function(json) {
        return _this.onMessage(json);
      };
    })(this)));
  };

  MazeGame.prototype.stop = function() {
    return this.client.disconnect();
  };

  MazeGame.prototype.reset = function() {
    this.client.reset();
    return this.client.enableDebug();
  };

  MazeGame.prototype.onMessage = function(json) {
    var payload;
    switch (json["action"]) {
      case "reset":
        return this.initializeBoard();
      case "initializeBoard":
        return this.initializeTiledBoardArea();
      case "initializeTiledBoardArea":
        return this.ready();
      case "brickFoundAtPosition":
        return this.brickFoundAtPosition(payload = json["payload"]);
      case "brickMovedToPosition":
        return this.brickMovedToPosition(payload = json["payload"]);
    }
  };

  MazeGame.prototype.startNewGame = function() {
    this.gameState = GameState.INITIALIZING;
    this.visibleLayer = 0;
    this.tileLayers[0].alpha = 0.0;
    this.tileLayers[1].alpha = 0.0;
    this.treasure.alpha = 0.0;
    this.resetMaze();
    return setTimeout((function(_this) {
      return function() {
        var fadeLogoTween;
        fadeLogoTween = _this.kiwiState.game.tweens.create(_this.logo);
        return fadeLogoTween.to({
          alpha: 1.0
        }, 2000, Kiwi.Animations.Tweens.Easing.Linear.In, true);
      };
    })(this), 500);
  };

  MazeGame.prototype.setupUi = function() {
    var content;
    content = document.getElementById("content");
    content.style.visibility = "visible";
    this.logo = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.logo, 0, 0);
    this.logo.alpha = 0.0;
    this.treasure = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.treasure, 0, 0);
    this.treasure.alpha = 0.0;
    this.treasure.anchorPointX = 0.0;
    this.treasure.anchorPointY = 0.0;
    this.tilemap = new Kiwi.GameObjects.Tilemap.TileMap(this.kiwiState, "tilemap", this.kiwiState.textures.tiles);
    this.borderLayer = this.tilemap.getLayerByName("Border Layer");
    this.tileLayers = [];
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 1"));
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 2"));
    this.kiwiState.addChild(this.borderLayer);
    this.kiwiState.addChild(this.tileLayers[0]);
    this.kiwiState.addChild(this.tileLayers[1]);
    this.kiwiState.addChild(this.treasure);
    return this.kiwiState.addChild(this.logo);

    /*
    statusTextField = new Kiwi.HUD.Widget.TextField(@kiwiState.game, "", 100, 10)
    statusTextField.style.color = "#00ff00"
    statusTextField.style.fontSize = "14px"
    statusTextField.style.textShadow = "-1px -1px 5px black, 1px -1px 5px black, -1px 1px 5px black, 1px 1px 5px black"
    @client.debug_textField = statusTextField
    @kiwiState.game.huds.defaultHUD.addWidget(statusTextField)
     */
  };

  MazeGame.prototype.initializeBoard = function() {
    return this.client.initializeBoard();
  };

  MazeGame.prototype.initializeTiledBoardArea = function() {
    return this.client.initializeTiledBoardArea(this.mazeModel.width, this.mazeModel.height, 0.0, 0.0, 1.0, 1.0, 0);
  };

  MazeGame.prototype.waitForStartPositions = function() {
    var j, len, player, ref, results;
    ref = this.mazeModel.players;
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      player = ref[j];
      results.push(this.requestPlayerInitialPosition(player));
    }
    return results;
  };

  MazeGame.prototype.brickFoundAtPosition = function(payload) {
    var player, position;
    player = this.mazeModel.players[payload["id"]];
    position = new Position(payload["position"][0], payload["position"][1]);
    return this.playerPlacedInitialBrick(player, position);
  };

  MazeGame.prototype.brickMovedToPosition = function(payload) {
    var player, position;
    player = this.mazeModel.players[payload["id"]];
    position = new Position(payload["position"][0], payload["position"][1]);
    switch (this.gameState) {
      case GameState.INITIAL_PLACEMENT:
        if (position.equals(player.position)) {
          return this.playerPlacedInitialBrick(player, position);
        } else {
          return this.playerMovedInitialBrick(player, position);
        }
        break;
      case GameState.PLAYING_GAME:
        if (player.index === this.currentPlayer.index) {
          return this.playerMovedBrick(position);
        }
    }
  };

  MazeGame.prototype.playerPlacedInitialBrick = function(player, position) {
    player.state = PlayerState.IDLE;
    player.reachDistance = playerDefaultReachDistance;
    this.updateMaze();
    return setTimeout((function(_this) {
      return function() {
        return _this.requestPlayerPosition(player);
      };
    })(this), 1500);
  };

  MazeGame.prototype.playerMovedInitialBrick = function(player, position) {
    var aPlayer, fadeLogoTween, j, len, p, ref;
    ref = this.mazeModel.players;
    for (j = 0, len = ref.length; j < len; j++) {
      aPlayer = ref[j];
      if (aPlayer.state !== PlayerState.IDLE) {
        aPlayer.state = PlayerState.DISABLED;
      }
    }
    this.gameState = GameState.PLAYING_GAME;
    fadeLogoTween = this.kiwiState.game.tweens.create(this.logo);
    fadeLogoTween.to({
      alpha: 0.0
    }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true);
    p = this.positionOnMap(this.mazeModel.treasurePosition.x, this.mazeModel.treasurePosition.y);
    this.treasure.x = p.x;
    this.treasure.y = p.y;
    setTimeout((function(_this) {
      return function() {
        var fadeTreasureTween;
        fadeTreasureTween = _this.kiwiState.game.tweens.create(_this.treasure);
        return fadeTreasureTween.to({
          alpha: 1.0
        }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true);
      };
    })(this), 1000);
    player.state = PlayerState.TURN;
    this.currentPlayer = player;
    return this.playerMovedBrick(position);
  };

  MazeGame.prototype.playerMovedBrick = function(position) {
    var oldPosition;
    this.client.resetReporters();
    oldPosition = this.currentPlayer.position;
    this.currentPlayer.position = position;
    this.updateMaze();
    if (this.currentPlayer.position.equals(this.mazeModel.treasurePosition)) {
      return this.playerDidFindTreasure(oldPosition);
    } else {
      return this.nextPlayerTurn();
    }
  };

  MazeGame.prototype.playerDidFindTreasure = function(fromPosition) {
    setTimeout((function(_this) {
      return function() {
        var moveTreasureTween, p;
        p = _this.positionOnMap(fromPosition.x, fromPosition.y);
        moveTreasureTween = _this.kiwiState.game.tweens.create(_this.treasure);
        return moveTreasureTween.to({
          x: p.x,
          y: p.y
        }, 1000, Kiwi.Animations.Tweens.Easing.Quadratic.InOut, true);
      };
    })(this), 1000);
    setTimeout((function(_this) {
      return function() {
        var fadeTreasureTween, j, len, player, ref;
        ref = _this.mazeModel.players;
        for (j = 0, len = ref.length; j < len; j++) {
          player = ref[j];
          player.state = PlayerState.DISABLED;
        }
        fadeTreasureTween = _this.kiwiState.game.tweens.create(_this.treasure);
        fadeTreasureTween.to({
          alpha: 0.0
        }, 2000, Kiwi.Animations.Tweens.Easing.Linear.In, true);
        _this.clearMaze();
        return _this.updateMaze();
      };
    })(this), 4000);
    return setTimeout((function(_this) {
      return function() {
        _this.startNewGame();
        return _this.reset();
      };
    })(this), 7000);
  };

  MazeGame.prototype.requestPlayerInitialPosition = function(player) {
    var position, positions;
    positions = (function() {
      var j, len, ref, results;
      ref = this.mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2);
      results = [];
      for (j = 0, len = ref.length; j < len; j++) {
        position = ref[j];
        results.push([position.x, position.y]);
      }
      return results;
    }).call(this);
    return this.client.reportBackWhenBrickMovedToPosition(0, [player.position.x, player.position.y], positions, player.index);
  };

  MazeGame.prototype.requestPlayerPosition = function(player) {
    var j, len, otherPlayer, playerPositions, position, positions, ref;
    playerPositions = this.mazeModel.positionsReachableByPlayer(player);
    ref = this.mazeModel.players;
    for (j = 0, len = ref.length; j < len; j++) {
      otherPlayer = ref[j];
      if (otherPlayer.state !== PlayerState.DISABLED) {
        playerPositions = (function() {
          var k, len1, results;
          results = [];
          for (k = 0, len1 = playerPositions.length; k < len1; k++) {
            position = playerPositions[k];
            if (!position.equals(otherPlayer.position)) {
              results.push(position);
            }
          }
          return results;
        })();
      }
    }
    positions = (function() {
      var k, len1, results;
      results = [];
      for (k = 0, len1 = playerPositions.length; k < len1; k++) {
        position = playerPositions[k];
        results.push([position.x, position.y]);
      }
      return results;
    })();
    return this.client.reportBackWhenBrickMovedToAnyOfPositions(0, [player.position.x, player.position.y], positions, player.index);
  };

  MazeGame.prototype.ready = function() {
    setTimeout((function(_this) {
      return function() {
        return _this.updateMaze();
      };
    })(this), 1500);
    return setTimeout((function(_this) {
      return function() {
        return _this.waitForStartPositions();
      };
    })(this), 2500);
  };

  MazeGame.prototype.resetMaze = function() {
    this.clearMaze();
    this.tileLayers[0].alpha = 1.0;
    this.mazeModel.createRandomMaze();
    this.gameState = GameState.INITIAL_PLACEMENT;
    this.currentPlayer = this.mazeModel.players[0];
    return this.isUpdatingMaze = false;
  };

  MazeGame.prototype.nextPlayerTurn = function() {
    var index, j, len, player, ref;
    index = this.currentPlayer.index;
    while (true) {
      index = (index + 1) % this.mazeModel.players.length;
      if (this.mazeModel.players[index].state !== PlayerState.DISABLED) {
        this.currentPlayer = this.mazeModel.players[index];
        break;
      }
    }
    ref = this.mazeModel.players;
    for (j = 0, len = ref.length; j < len; j++) {
      player = ref[j];
      if (player.state !== PlayerState.DISABLED) {
        player.state = PlayerState.IDLE;
      }
    }
    this.currentPlayer.state = PlayerState.TURN;
    this.updateMaze();
    return setTimeout((function(_this) {
      return function() {
        return _this.requestPlayerPosition(_this.currentPlayer);
      };
    })(this), 2000);
  };

  MazeGame.prototype.clearMaze = function() {
    var j, k, ref, ref1, x, y;
    for (y = j = 0, ref = this.mazeModel.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      for (x = k = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
        this.tileLayers[this.visibleLayer].setTile(x, y, transparentTileIndex);
      }
    }
    return this.drawMaze();
  };

  MazeGame.prototype.updateMaze = function() {
    var destinationAlpha, fadeMazeTween;
    if (this.isUpdatingMaze) {
      setTimeout((function(_this) {
        return function() {
          return _this.updateMaze();
        };
      })(this), 1500);
      return;
    }
    this.isUpdatingMaze = true;
    this.visibleLayer = this.visibleLayer === 0 ? 1 : 0;
    this.drawMaze();
    destinationAlpha = this.visibleLayer === 0 ? 0.0 : 1.0;
    fadeMazeTween = this.kiwiState.game.tweens.create(this.tileLayers[1]);
    fadeMazeTween.to({
      alpha: destinationAlpha
    }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true);
    return setTimeout((function(_this) {
      return function() {
        return _this.isUpdatingMaze = false;
      };
    })(this), 1000);
  };

  MazeGame.prototype.drawMaze = function() {
    var drawOrder, entry, i, j, k, l, len, len1, m, player, playerIndex, position, ref, ref1, ref2, results, tileIndex, x, y;
    for (y = j = 0, ref = this.mazeModel.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      for (x = k = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
        tileIndex = this.mazeModel.isBorderAtCoordinate(x, y) ? transparentTileIndex : blackTileIndex;
        this.tileLayers[this.visibleLayer].setTile(x, y, tileIndex);
      }
    }
    if (this.mazeModel.players == null) {
      return;
    }
    drawOrder = (function() {
      var l, ref2, results;
      results = [];
      for (i = l = 0, ref2 = this.mazeModel.players.length - 1; 0 <= ref2 ? l <= ref2 : l >= ref2; i = 0 <= ref2 ? ++l : --l) {
        results.push(i);
      }
      return results;
    }).call(this);
    drawOrder.splice(this.currentPlayer.index, 1);
    drawOrder.push(this.currentPlayer.index);
    results = [];
    for (l = 0, len = drawOrder.length; l < len; l++) {
      playerIndex = drawOrder[l];
      player = this.mazeModel.players[playerIndex];
      if (player.state === PlayerState.DISABLED) {
        continue;
      }
      ref2 = this.mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2);
      for (m = 0, len1 = ref2.length; m < len1; m++) {
        position = ref2[m];
        entry = this.mazeModel.entryAtPosition(position);
        this.tileLayers[this.visibleLayer].setTile(position.x, position.y, entry.tileIndex + darkenTileOffset);
      }
      results.push((function() {
        var len2, n, ref3, results1;
        ref3 = this.mazeModel.positionsReachableFromPosition(player.position, player.reachDistance);
        results1 = [];
        for (n = 0, len2 = ref3.length; n < len2; n++) {
          position = ref3[n];
          entry = this.mazeModel.entryAtPosition(position);
          results1.push(this.tileLayers[this.visibleLayer].setTile(position.x, position.y, entry.tileIndex + this.tileOffset(player, position)));
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeGame.prototype.tileOffset = function(player, position) {
    switch (this.gameState) {
      case GameState.INITIAL_PLACEMENT:
        if (player.state === PlayerState.INITIAL_PLACEMENT) {
          if (player.position.equals(position)) {
            return 0;
          } else {
            return darkenTileOffset;
          }
        } else {
          return 0;
        }
        break;
      case GameState.PLAYING_GAME:
        if (this.currentPlayer.index === player.index) {
          return 0;
        } else {
          return darkenTileOffset;
        }
        break;
      default:
        return 0;
    }
  };

  MazeGame.prototype.positionOnMap = function(position) {
    return this.positionOnMap(position.x, position.y);
  };

  MazeGame.prototype.positionOnMap = function(x, y) {
    return new Position((this.kiwiState.game.stage.width * x) / this.mazeModel.width, (this.kiwiState.game.stage.height * y) / this.mazeModel.height);
  };

  return MazeGame;

})();

//# sourceMappingURL=game.js.map
