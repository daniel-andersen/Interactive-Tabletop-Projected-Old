var GameState, MAZE, MazeGame, mazeGame, tileLayers;

MAZE = MAZE || {};

MAZE.Game = new Kiwi.State("Game");

tileLayers = [];

mazeGame = null;

MAZE.Game.preload = function() {
  this.addJSON("tilemap", "assets/maps/maze.json");
  this.addSpriteSheet("tiles", "assets/img/tiles/board_tiles.png", 40, 40);
  return this.addImage("logo", "assets/img/menu/title.png");
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
  PLAYER_TURN: 2
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
    return this.client.reset();
  };

  MazeGame.prototype.onMessage = function(json) {
    switch (json["action"]) {
      case "reset":
        return this.initializeBoard();
      case "initializeTiledBoard":
        return this.ready();
    }
  };

  MazeGame.prototype.startNewGame = function() {
    this.gameState = GameState.INITIALIZING;
    this.currentPlayerIndex = 0;
    this.visibleLayer = 0;
    this.tileLayers[0].alpha = 1.0;
    this.tileLayers[1].alpha = 0.0;
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
    var statusTextField;
    this.logo = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.logo, 0, 0);
    this.logo.alpha = 0.0;
    this.tilemap = new Kiwi.GameObjects.Tilemap.TileMap(this.kiwiState, "tilemap", this.kiwiState.textures.tiles);
    this.borderLayer = this.tilemap.getLayerByName("Border Layer");
    this.tileLayers = [];
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 1"));
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 2"));
    this.kiwiState.addChild(this.borderLayer);
    this.kiwiState.addChild(this.tileLayers[0]);
    this.kiwiState.addChild(this.tileLayers[1]);
    this.kiwiState.addChild(this.logo);
    statusTextField = new Kiwi.HUD.Widget.TextField(this.kiwiState.game, "", 100, 10);
    statusTextField.style.color = "#00ff00";
    statusTextField.style.fontSize = "14px";
    statusTextField.style.textShadow = "-1px -1px 5px black, 1px -1px 5px black, -1px 1px 5px black, 1px 1px 5px black";
    this.client.debug_textField = statusTextField;
    return this.kiwiState.game.huds.defaultHUD.addWidget(statusTextField);
  };

  MazeGame.prototype.initializeBoard = function() {
    return this.client.initializeTiledBoard(this.mazeModel.width, this.mazeModel.height);
  };

  MazeGame.prototype.waitForStartPositions = function() {
    var i, id, j, position, positions, ref, results;
    results = [];
    for (i = j = 0, ref = this.mazeModel.players.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
      positions = (function() {
        var k, len, ref1, results1;
        ref1 = this.mazeModel.positionsReachableByPlayer(this.mazeModel.players[i]);
        results1 = [];
        for (k = 0, len = ref1.length; k < len; k++) {
          position = ref1[k];
          results1.push([position.x, position.y]);
        }
        return results1;
      }).call(this);
      results.push(this.client.reportBackWhenTileAtAnyOfPositions(positions, id = i));
    }
    return results;
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
    var j, k, ref, ref1, x, y;
    for (y = j = 0, ref = this.mazeModel.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      for (x = k = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
        this.tileLayers[this.visibleLayer].setTile(x, y, transparentTileIndex);
      }
    }
    this.mazeModel.createRandomMaze();
    return this.gameState = GameState.INITIAL_PLACEMENT;
  };

  MazeGame.prototype.updateMaze = function() {
    var destinationAlpha, fadeMazeTween;
    this.visibleLayer = this.visibleLayer === 0 ? 1 : 0;
    this.drawMaze();
    destinationAlpha = this.visibleLayer === 0 ? 0.0 : 1.0;
    fadeMazeTween = this.kiwiState.game.tweens.create(this.tileLayers[1]);
    return fadeMazeTween.to({
      alpha: destinationAlpha
    }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true);
  };

  MazeGame.prototype.drawMaze = function() {
    var drawOrder, entry, i, j, k, l, len, player, playerIndex, position, ref, ref1, results, x, y;
    for (y = j = 0, ref = this.mazeModel.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      for (x = k = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
        this.tileLayers[this.visibleLayer].setTile(x, y, transparentTileIndex);
      }
    }
    drawOrder = (function() {
      var l, ref2, results;
      results = [];
      for (i = l = 0, ref2 = this.mazeModel.numberOfPlayers - 1; 0 <= ref2 ? l <= ref2 : l >= ref2; i = 0 <= ref2 ? ++l : --l) {
        results.push(i);
      }
      return results;
    }).call(this);
    drawOrder.splice(this.currentPlayerIndex, 1);
    drawOrder.push(this.currentPlayerIndex);
    results = [];
    for (l = 0, len = drawOrder.length; l < len; l++) {
      playerIndex = drawOrder[l];
      player = this.mazeModel.players[playerIndex];
      results.push((function() {
        var len1, m, ref2, results1;
        ref2 = this.mazeModel.positionsReachableByPlayer(player);
        results1 = [];
        for (m = 0, len1 = ref2.length; m < len1; m++) {
          position = ref2[m];
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
        if (player.position.equals(position)) {
          return 0;
        } else {
          return darkenTileOffset;
        }
        break;
      default:
        return 0;
    }
  };

  return MazeGame;

})();

//# sourceMappingURL=game.js.map
