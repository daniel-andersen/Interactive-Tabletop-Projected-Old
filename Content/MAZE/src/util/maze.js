var Maze;

Maze = (function() {
  function Maze(kiwiState) {
    this.kiwiState = kiwiState;
    this.client = new Client();
  }

  Maze.prototype.start = function() {
    this.setupUi();
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

  Maze.prototype.stop = function() {
    return this.client.disconnect();
  };

  Maze.prototype.reset = function() {
    return this.client.reset();
  };

  Maze.prototype.onMessage = function(json) {
    switch (json["action"]) {
      case "reset":
        return this.initializeBoard();
      case "initializeTiledBoard":
        return this.ready();
    }
  };

  Maze.prototype.setupUi = function() {
    var borderLayer, i, len, ref, statusTextField, tileLayer;
    this.tilemap = new Kiwi.GameObjects.Tilemap.TileMap(this.kiwiState, "tilemap", this.kiwiState.textures.tiles);
    borderLayer = this.tilemap.getLayerByName("Border Layer");
    this.tileLayers = [];
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 1"));
    this.tileLayers.push(this.tilemap.getLayerByName("Tile Layer 2"));
    ref = this.tileLayers;
    for (i = 0, len = ref.length; i < len; i++) {
      tileLayer = ref[i];
      tileLayer.alpha = 0.0;
    }
    this.kiwiState.addChild(borderLayer);
    this.kiwiState.addChild(this.tileLayers[0]);
    this.kiwiState.addChild(this.tileLayers[1]);
    statusTextField = new Kiwi.HUD.Widget.TextField(this.kiwiState.game, "HEY 2", 100, 10);
    statusTextField.style.color = "#00ff00";
    statusTextField.style.fontSize = "14px";
    statusTextField.style.textShadow = "-1px -1px 5px black, 1px -1px 5px black, -1px 1px 5px black, 1px 1px 5px black";
    this.client.debug_textField = statusTextField;
    return this.kiwiState.game.huds.defaultHUD.addWidget(statusTextField);
  };

  Maze.prototype.initializeBoard = function() {
    return this.client.initializeTiledBoard(32, 20);
  };

  Maze.prototype.waitForStartPositions = function() {
    return this.client.reportBackWhenTileAtAnyOfPositions([[10, 10], [11, 10], [12, 10]]);
  };

  Maze.prototype.ready = function() {
    console.log("Ready!");
    return this.waitForStartPositions();
  };

  return Maze;

})();

//# sourceMappingURL=maze.js.map
