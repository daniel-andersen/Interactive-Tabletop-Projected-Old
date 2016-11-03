var EXAMPLE4, Example4Game, example4Game;

EXAMPLE4 = EXAMPLE4 || {};

EXAMPLE4.Game = new Kiwi.State("Game");

example4Game = null;

EXAMPLE4.Game.preload = function() {
  this.addImage("corners", "assets/img/game/corners.png");
  this.addImage("box", "assets/img/game/box.png");
  return this.addImage("marker_23", "assets/img/game/23.png");
};

EXAMPLE4.Game.create = function() {
  Kiwi.State.prototype.create.call(this);
  example4Game = new Example4Game(this);
  return example4Game.start();
};

EXAMPLE4.Game.shutDown = function() {
  Kiwi.State.prototype.shutDown.call(this);
  return example4Game.stop();
};

EXAMPLE4.Game.update = function() {
  Kiwi.State.prototype.update.call(this);
  return example4Game.update();
};

Example4Game = (function() {
  function Example4Game(kiwiState) {
    this.kiwiState = kiwiState;
    this.client = new Client();
    this.scaleAnimCounter = 0.0;
    this.aruco_marker_23 = void 0;
  }

  Example4Game.prototype.start = function() {
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

  Example4Game.prototype.stop = function() {
    return this.client.disconnect();
  };

  Example4Game.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.initializeBoard();
      };
    })(this));
  };

  Example4Game.prototype.onMessage = function(json) {};

  Example4Game.prototype.update = function() {
    this.scaleAnimCounter += 0.1;
    if (this.aruco_marker_23 != null) {
      return this.aruco_marker_23.scale = 1.0 + (Math.cos(this.scaleAnimCounter) * 0.1);
    }
  };

  Example4Game.prototype.setupUi = function() {
    var content;
    content = document.getElementById("content");
    content.style.visibility = "visible";
    this.corners = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.corners, 0, 0);
    return this.kiwiState.addChild(this.corners);
  };

  Example4Game.prototype.initializeBoard = function() {
    return this.client.initializeBoard(void 0, void 0, (function(_this) {
      return function(action, payload) {
        return _this.initializeBoardAreas();
      };
    })(this));
  };

  Example4Game.prototype.initializeBoardAreas = function() {
    this.wholeBoardAreaId = 0;
    return this.client.initializeBoardArea(0.0, 0.0, 1.0, 1.0, this.wholeBoardAreaId, (function(_this) {
      return function(action, payload) {
        return _this.initializeMarkers();
      };
    })(this));
  };

  Example4Game.prototype.initializeMarkers = function() {
    this.arUcoMarkerId = 0;
    return this.client.initializeArUcoMarker(this.arUcoMarkerId, 23, 6, void 0, (function(_this) {
      return function(action, payload) {
        return _this.startNewGame();
      };
    })(this));
  };

  Example4Game.prototype.startNewGame = function() {
    this.client.requestArUcoMarkers(this.wholeBoardAreaId, 6, void 0, (function(_this) {
      return function(action, payload) {
        var angle, box, i, len, marker, position, ref, results;
        ref = payload["markers"];
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
          marker = ref[i];
          box = new Kiwi.GameObjects.Sprite(_this.kiwiState, _this.kiwiState.textures.box, 0, 0);
          _this.kiwiState.addChild(box);
          position = new Position(marker["x"], marker["y"]);
          angle = marker["angle"];
          box.x = (_this.kiwiState.game.stage.width * position.x) - (box.width / 2.0);
          box.y = (_this.kiwiState.game.stage.height * position.y) - (box.height / 2.0);
          results.push(box.rotation = angle * Math.PI / 180.0);
        }
        return results;
      };
    })(this));
    return this.client.reportBackWhenMarkerFound(this.wholeBoardAreaId, this.arUcoMarkerId, void 0, void 0, (function(_this) {
      return function(action, payload) {
        var angle, position;
        position = new Position(payload["marker"]["x"], payload["marker"]["y"]);
        angle = payload["marker"]["angle"];
        _this.aruco_marker_23 = new Kiwi.GameObjects.Sprite(_this.kiwiState, _this.kiwiState.textures.marker_23, 0, 0);
        _this.kiwiState.addChild(_this.aruco_marker_23);
        _this.aruco_marker_23.x = (_this.kiwiState.game.stage.width * position.x) - (_this.aruco_marker_23.width / 2.0);
        _this.aruco_marker_23.y = (_this.kiwiState.game.stage.height * position.y) - (_this.aruco_marker_23.height / 2.0);
        return _this.aruco_marker_23.rotation = angle * Math.PI / 180.0;
      };
    })(this));
  };

  return Example4Game;

})();

//# sourceMappingURL=game.js.map
