var EXAMPLE2, Example2Game, example2Game;

EXAMPLE2 = EXAMPLE2 || {};

EXAMPLE2.Game = new Kiwi.State("Game");

example2Game = null;

EXAMPLE2.Game.preload = function() {
  this.addImage("corners", "assets/img/game/corners.png");
  return this.addImage("marker_next", "assets/img/game/marker_next.png");
};

EXAMPLE2.Game.create = function() {
  Kiwi.State.prototype.create.call(this);
  example2Game = new Example2Game(this);
  return example2Game.start();
};

EXAMPLE2.Game.shutDown = function() {
  Kiwi.State.prototype.shutDown.call(this);
  return example2Game.stop();
};

EXAMPLE2.Game.update = function() {
  Kiwi.State.prototype.update.call(this);
  return example2Game.update();
};

Example2Game = (function() {
  function Example2Game(kiwiState) {
    this.kiwiState = kiwiState;
    this.client = new Client();
    this.scaleAnimCounter = 0.0;
  }

  Example2Game.prototype.start = function() {
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

  Example2Game.prototype.stop = function() {
    return this.client.disconnect();
  };

  Example2Game.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.initializeBoard();
      };
    })(this));
  };

  Example2Game.prototype.onMessage = function(json) {};

  Example2Game.prototype.update = function() {
    this.scaleAnimCounter += 0.1;
    return this.next_marker.scale = 1.0 + (Math.cos(this.scaleAnimCounter) * 0.1);
  };

  Example2Game.prototype.setupUi = function() {
    var content;
    content = document.getElementById("content");
    content.style.visibility = "visible";
    this.corners = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.corners, 0, 0);
    this.kiwiState.addChild(this.corners);
    this.next_marker = new Kiwi.GameObjects.Sprite(this.kiwiState, this.kiwiState.textures.marker_next, 0, 0);
    this.next_marker.visible = false;
    return this.kiwiState.addChild(this.next_marker);
  };

  Example2Game.prototype.initializeBoard = function() {
    return this.client.initializeBoard(void 0, void 0, (function(_this) {
      return function(action, payload) {
        return _this.initializeBoardAreas();
      };
    })(this));
  };

  Example2Game.prototype.initializeBoardAreas = function() {
    this.wholeBoardAreaId = 0;
    return this.client.initializeBoardArea(0.0, 0.0, 1.0, 1.0, this.wholeBoardAreaId, (function(_this) {
      return function(action, payload) {
        return _this.initializeMarkers();
      };
    })(this));
  };

  Example2Game.prototype.initializeMarkers = function() {
    var image1;
    this.nextMarkerId = 0;
    image1 = new Image();
    image1.onload = (function(_this) {
      return function() {
        return _this.client.initializeShapeMarkerWithImage(_this.nextMarkerId, image1, 0.001, 0.4, function(action, payload) {
          return _this.startNewGame();
        });
      };
    })(this);
    return image1.src = "assets/tracking/marker_next.png";
  };

  Example2Game.prototype.startNewGame = function() {
    return this.client.reportBackWhenMarkerFound(this.wholeBoardAreaId, this.nextMarkerId, void 0, void 0, (function(_this) {
      return function(action, payload) {
        return _this.client.startTrackingMarker(_this.wholeBoardAreaId, _this.nextMarkerId, void 0, function(action, payload) {
          var angle, position;
          position = new Position(payload["marker"]["x"], payload["marker"]["y"]);
          angle = payload["marker"]["angle"];
          _this.next_marker.x = (_this.kiwiState.game.stage.width * position.x) - (_this.next_marker.width / 2.0);
          _this.next_marker.y = (_this.kiwiState.game.stage.height * position.y) - (_this.next_marker.height / 2.0);
          _this.next_marker.rotation = angle * Math.PI / 180.0;
          _this.next_marker.visible = true;
          return false;
        });
      };
    })(this));
  };

  return Example2Game;

})();

//# sourceMappingURL=game.js.map
