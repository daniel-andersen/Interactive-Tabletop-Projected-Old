var Client;

Client = (function() {
  var action, payload, socket;

  socket = null;

  action = "action";

  payload = "payload";

  function Client(port) {
    this.port = port != null ? port : 9001;
    this.debug_textField = null;
    this.debug_log = [];
    this.socketOpen = false;
  }

  Client.prototype.connect = function(onSocketOpen, onMessage) {
    this.disconnect();
    this.socket = new WebSocket("ws://localhost:" + this.port + "/");
    this.socket.onopen = (function(_this) {
      return function(event) {
        return onSocketOpen();
      };
    })(this);
    return this.socket.onmessage = (function(_this) {
      return function(event) {
        var json;
        json = JSON.parse(event.data);
        onMessage(json);
        if (_this.debug_textField != null) {
          _this.debug_log.splice(0, 0, JSON.stringify(json));
          return _this.debug_textField.text = _this.debug_log.slice(0, 6).join("<br/>");
        }
      };
    })(this);
  };

  Client.prototype.disconnect = function() {
    if (this.socket) {
      this.socket.close();
      return this.socket = null;
    }
  };

  Client.prototype.enableDebug = function() {
    return this.sendMessage("enableDebug", {});
  };

  Client.prototype.reset = function(resolution) {
    if (resolution == null) {
      resolution = null;
    }
    if (resolution != null) {
      return this.sendMessage("reset", {
        "resolution": resolution
      });
    } else {
      return this.sendMessage("reset", {});
    }
  };

  Client.prototype.resetReporters = function() {
    return this.sendMessage("resetReporters", {});
  };

  Client.prototype.resetReporter = function(reporterId) {
    return this.sendMessage("resetReporter", {
      "id": reporterId
    });
  };

  Client.prototype.takeScreenshot = function(filename) {
    if (filename == null) {
      filename = null;
    }
    if (filename !== null) {
      return this.sendMessage("takeScreenshot", {
        "filename": filename
      });
    } else {
      return this.sendMessage("takeScreenshot", {});
    }
  };

  Client.prototype.initializeTiledBoard = function(tileCountX, tileCountY, borderPctX, borderPctY, cornerMarker) {
    if (borderPctX == null) {
      borderPctX = 0.0;
    }
    if (borderPctY == null) {
      borderPctY = 0.0;
    }
    if (cornerMarker == null) {
      cornerMarker = "DEFAULT";
    }
    return this.sendMessage("initializeTiledBoard", {
      "tileCountX": tileCountX,
      "tileCountY": tileCountY,
      "borderPctX": borderPctX,
      "borderPctY": borderPctY,
      "cornerMarker": cornerMarker
    });
  };

  Client.prototype.initializeGenericBoard = function(borderPctX, borderPctY, cornerMarker) {
    if (borderPctX == null) {
      borderPctX = 0.0;
    }
    if (borderPctY == null) {
      borderPctY = 0.0;
    }
    if (cornerMarker == null) {
      cornerMarker = "DEFAULT";
    }
    return this.sendMessage("initializeGenericBoard", {
      "borderPctX": borderPctX,
      "borderPctY": borderPctY,
      "cornerMarker": cornerMarker
    });
  };

  Client.prototype.requestTiledObjectPosition = function(validPositions) {
    return this.sendMessage("requestBrickPosition", {
      "validPositions": validPositions
    });
  };

  Client.prototype.reportBackWhenBrickFoundAtAnyOfPositions = function(validPositions, id, stableTime) {
    if (id == null) {
      id = null;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    if (id !== null) {
      return this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
        "validPositions": validPositions,
        "stableTime": stableTime,
        "id": id
      });
    } else {
      return this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
        "validPositions": validPositions,
        "stableTime": stableTime
      });
    }
  };

  Client.prototype.reportBackWhenBrickMovedToAnyOfPositions = function(initialPosition, validPositions, id, stableTime) {
    if (id == null) {
      id = null;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    if (id !== null) {
      return this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
        "initialPosition": initialPosition,
        "validPositions": validPositions,
        "stableTime": stableTime,
        "id": id
      });
    } else {
      return this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
        "initialPosition": initialPosition,
        "validPositions": validPositions,
        "stableTime": stableTime
      });
    }
  };

  Client.prototype.reportBackWhenBrickMovedToPosition = function(position, validPositions, id, stableTime) {
    if (id == null) {
      id = null;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    if (id !== null) {
      return this.sendMessage("reportBackWhenBrickMovedToPosition", {
        "position": position,
        "validPositions": validPositions,
        "stableTime": stableTime,
        "id": id
      });
    } else {
      return this.sendMessage("reportBackWhenBrickMovedToPosition", {
        "position": position,
        "validPositions": validPositions,
        "stableTime": stableTime
      });
    }
  };

  Client.prototype.sendMessage = function(action, payload) {
    var message;
    message = {
      action: action,
      payload: payload
    };
    return this.socket.send(JSON.stringify(message));
  };

  return Client;

})();

//# sourceMappingURL=clientLibrary.js.map
