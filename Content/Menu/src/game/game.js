var MENU, MenuGame, WheelState, menuGame;

MENU = MENU || {};

MENU.Game = new Kiwi.State("Game");

menuGame = null;

MENU.Game.preload = function() {
  this.addImage("corners", "assets/img/game/corners.png");
  this.addImage("wheel_background", "assets/img/game/wheel_background.png");
  this.addImage("wheel_foreground", "assets/img/game/wheel_foreground.png");
  return this.addImage("wheel_marker", "assets/img/game/wheel_marker.png");
};

MENU.Game.create = function() {
  Kiwi.State.prototype.create.call(this);
  menuGame = new MenuGame(this);
  return menuGame.start();
};

MENU.Game.shutDown = function() {
  Kiwi.State.prototype.shutDown.call(this);
  return menuGame.stop();
};

MENU.Game.update = function() {
  Kiwi.State.prototype.update.call(this);
  return menuGame.update();
};

WheelState = {
  GONE: 0,
  POSITIONING: 1,
  SELECTING: 2
};

MenuGame = (function() {
  function MenuGame(kiwiState) {
    this.kiwiState = kiwiState;
    this.client = new Client();
  }

  MenuGame.prototype.start = function() {
    this.setup();
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

  MenuGame.prototype.stop = function() {
    return this.client.disconnect();
  };

  MenuGame.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.initializeBoard();
      };
    })(this));
  };

  MenuGame.prototype.onMessage = function(json) {};

  MenuGame.prototype.update = function() {};

  MenuGame.prototype.setup = function() {
    this.menuArUcoMarkerIndex = 50;
    this.selectionsCount = 8;
    this.markerRelaxationTime = 2.0;
    this.markerStableTime = 1.0;
    this.markerStableDistance = 0.02;
    this.markerStartAngle = void 0;
    this.markerHistory = [];
    this.wheelState = WheelState.GONE;
    return this.wheelPosition = void 0;
  };

  MenuGame.prototype.setupUi = function() {
    var content;
    content = document.getElementById("content");
    content.style.visibility = "visible";
    this.corners = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.corners, 0, 0);
    this.kiwiState.addChild(this.corners);
    this.wheelBackground = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.wheel_background, 0, 0);
    this.wheelBackground.visible = false;
    this.kiwiState.addChild(this.wheelBackground);
    this.wheelMarker = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.wheel_marker, 0, 0);
    this.wheelMarker.visible = false;
    this.kiwiState.addChild(this.wheelMarker);
    this.wheelForeground = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.wheel_foreground, 0, 0);
    this.wheelForeground.visible = false;
    return this.kiwiState.addChild(this.wheelForeground);
  };

  MenuGame.prototype.initializeBoard = function() {
    return this.client.initializeBoard(void 0, void 0, (function(_this) {
      return function(action, payload) {
        return _this.initializeBoardAreas();
      };
    })(this));
  };

  MenuGame.prototype.initializeBoardAreas = function() {
    this.wholeBoardAreaId = 0;
    return this.client.initializeBoardArea(0.0, 0.0, 1.0, 1.0, this.wholeBoardAreaId, (function(_this) {
      return function(action, payload) {
        return _this.startNewGame();
      };
    })(this));
  };

  MenuGame.prototype.startNewGame = function() {
    return setTimeout((function(_this) {
      return function() {
        return _this.findMarker();
      };
    })(this), 2000);
  };

  MenuGame.prototype.findMarker = function() {
    return this.client.requestArUcoMarkers(this.wholeBoardAreaId, 6, void 0, (function(_this) {
      return function(action, payload) {
        _this.foundMarkers(payload["markers"]);
        return _this.findMarker();
      };
    })(this));
  };

  MenuGame.prototype.foundMarkers = function(markers) {
    var i, len, m, marker;
    this.updateMarkerHistory();
    if (markers.length === 0) {
      return;
    }
    marker = void 0;
    for (i = 0, len = markers.length; i < len; i++) {
      m = markers[i];
      if (m["markerId"] === this.menuArUcoMarkerIndex) {
        marker = m;
      }
    }
    if (marker == null) {
      return;
    }
    this.markerHistory.push({
      "timestamp": Util.currentTimeSeconds(),
      "marker": marker
    });
    return this.updateWheel(marker);
  };

  MenuGame.prototype.updateWheel = function(marker) {
    if (this.wheelState === WheelState.GONE) {
      this.showWheel(marker);
      return;
    }
    if (this.wheelState === WheelState.POSITIONING) {
      this.updateWheelPosition(marker);
      return;
    }
    return this.updateSelectedAngle(marker);
  };

  MenuGame.prototype.showWheel = function(marker) {
    this.wheelState = WheelState.POSITIONING;
    this.updateWheelPosition(marker);
    this.wheelForeground.alpha = 0.0;
    this.wheelMarker.alpha = 0.0;
    return this.toggleWheel(true);
  };

  MenuGame.prototype.startSelecting = function() {
    this.wheelState = WheelState.SELECTING;
    Util.fadeInElement(this.wheelForeground, 500, this.kiwiState);
    return Util.fadeInElement(this.wheelMarker, 500, this.kiwiState, 250);
  };

  MenuGame.prototype.updateWheelPosition = function(marker) {
    var deltaPosition, i, lastMarker, len, m, moveDistance, ref;
    this.wheelPosition = this.wheelPositionFromMarker(marker);
    this.markerStartAngle = this.wheelAngleFromMarker(marker);
    this.wheelBackground.x = this.wheelPosition[0] - (this.wheelBackground.width / 2.0);
    this.wheelBackground.y = this.wheelPosition[1] - (this.wheelBackground.height / 2.0);
    this.wheelBackground.rotation = 0.0;
    this.wheelMarker.x = this.wheelPosition[0] - (this.wheelMarker.width / 2.0);
    this.wheelMarker.y = this.wheelPosition[1] - (this.wheelMarker.height / 2.0);
    this.wheelMarker.rotation = 0.0;
    this.wheelForeground.x = this.wheelPosition[0] - (this.wheelForeground.width / 2.0);
    this.wheelForeground.y = this.wheelPosition[1] - (this.wheelForeground.height / 2.0);
    this.wheelForeground.rotation = 0.0;
    lastMarker = void 0;
    ref = this.markerHistory;
    for (i = 0, len = ref.length; i < len; i++) {
      m = ref[i];
      if (m["timestamp"] < Util.currentTimeSeconds() - this.markerStableTime) {
        lastMarker = m["marker"];
      }
    }
    if (lastMarker != null) {
      deltaPosition = [lastMarker["x"] - marker["x"], lastMarker["y"] - marker["y"]];
      moveDistance = Math.sqrt(deltaPosition[0] * deltaPosition[0] + deltaPosition[1] * deltaPosition[1]);
      if (moveDistance < this.markerStableDistance) {
        return this.startSelecting();
      }
    }
  };

  MenuGame.prototype.updateSelectedAngle = function(marker) {
    this.wheelSelection = Math.round((Util.angleDifference(this.wheelAngleFromMarker(marker), this.markerStartAngle) / (Math.PI * 2.0)) * this.selectionsCount) % this.selectionsCount;
    this.wheelMarker.rotation = this.wheelSelection * Math.PI * 2.0 / this.selectionsCount;
    return console.log("Wheel selection: " + this.wheelSelection);
  };

  MenuGame.prototype.updateMarkerHistory = function() {
    while (this.markerHistory.length > 0 && this.markerHistory[0]["timestamp"] < Util.currentTimeSeconds() - this.markerRelaxationTime) {
      this.markerHistory.shift();
    }
    if (this.markerHistory.length === 0) {
      this.toggleWheel(false);
      return this.wheelState = WheelState.GONE;
    }
  };

  MenuGame.prototype.toggleWheel = function(toggle) {
    this.wheelBackground.visible = toggle;
    this.wheelMarker.visible = toggle;
    return this.wheelForeground.visible = toggle;
  };

  MenuGame.prototype.wheelPositionFromMarker = function(marker) {
    return [marker["x"] * this.kiwiState.game.stage.width, marker["y"] * this.kiwiState.game.stage.height];
  };

  MenuGame.prototype.wheelAngleFromMarker = function(marker) {
    return marker["angle"] * Math.PI / 180.0;
  };

  return MenuGame;

})();

//# sourceMappingURL=game.js.map
