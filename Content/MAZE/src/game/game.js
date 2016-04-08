var MAZE, MazeGame, mazeGame, tileLayers;

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

MazeGame = (function() {
  function MazeGame(kiwiState) {
    this.kiwiState = kiwiState;
    this.client = new Client();
    this.mazeModel = new MazeModel();
  }

  MazeGame.prototype.start = function() {
    this.setupUi();
    console.log("1");
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

  MazeGame.prototype.setupUi = function() {
    var borderLayer, statusTextField;
    this.logo = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.logo, 0, 0);
    this.logo.alpha = 0.0;
    this.tilemap = new Kiwi.GameObjects.Tilemap.TileMap(this.kiwiState, "tilemap", this.kiwiState.textures.tiles);
    borderLayer = this.tilemap.getLayerByName("Border Layer");
    this.tileLayers = [];
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 1"));
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 2"));
    this.tileLayers[0].alpha = 1.0;
    this.tileLayers[1].alpha = 0.0;
    this.visibleLayer = 0;
    this.kiwiState.addChild(borderLayer);
    this.kiwiState.addChild(this.tileLayers[0]);
    this.kiwiState.addChild(this.tileLayers[1]);
    this.kiwiState.addChild(this.logo);
    statusTextField = new Kiwi.HUD.Widget.TextField(this.kiwiState.game, "", 100, 10);
    statusTextField.style.color = "#00ff00";
    statusTextField.style.fontSize = "14px";
    statusTextField.style.textShadow = "-1px -1px 5px black, 1px -1px 5px black, -1px 1px 5px black, 1px 1px 5px black";
    this.client.debug_textField = statusTextField;
    this.kiwiState.game.huds.defaultHUD.addWidget(statusTextField);
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

  MazeGame.prototype.initializeBoard = function() {
    return this.client.initializeTiledBoard(this.mazeModel.width, this.mazeModel.height);
  };

  MazeGame.prototype.waitForStartPositions = function() {
    return this.client.reportBackWhenTileAtAnyOfPositions([[10, 10], [11, 10], [12, 10]]);
  };

  MazeGame.prototype.ready = function() {
    console.log("2");
    setTimeout((function(_this) {
      return function() {
        _this.mazeModel.createRandomMaze();
        return _this.updateMaze();
      };
    })(this), 1500);
    return setTimeout((function(_this) {
      return function() {
        return _this.waitForStartPositions();
      };
    })(this), 2500);
  };

  MazeGame.prototype.updateMaze = function() {
    var alpha, entry, fadeMazeTween, i, j, ref, ref1, x, y;
    this.visibleLayer = this.visibleLayer === 0 ? 1 : 0;
    for (y = i = 0, ref = this.mazeModel.height - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
      for (x = j = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
        entry = this.mazeModel.entryAtCoordinate(x, y);
        this.tileLayers[this.visibleLayer].setTile(x, y, entry.tileIndex);
      }
    }
    alpha = this.visibleLayer === 0 ? 0.0 : 1.0;
    fadeMazeTween = this.kiwiState.game.tweens.create(this.tileLayers[1]);
    return fadeMazeTween.to({
      alpha: alpha
    }, 1000, Kiwi.Animations.Tweens.Easing.Linear.In, true);
  };

  return MazeGame;

})();

//# sourceMappingURL=game.js.map
