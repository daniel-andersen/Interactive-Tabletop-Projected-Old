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
      filename = void 0;
    }
    if (filename !== void 0) {
      return this.sendMessage("takeScreenshot", {
        "filename": filename
      });
    } else {
      return this.sendMessage("takeScreenshot", {});
    }
  };

  Client.prototype.initializeBoard = function(borderPctX, borderPctY, cornerMarker) {
    if (borderPctX == null) {
      borderPctX = 0.0;
    }
    if (borderPctY == null) {
      borderPctY = 0.0;
    }
    if (cornerMarker == null) {
      cornerMarker = "DEFAULT";
    }
    return this.sendMessage("initializeBoard", {
      "borderPctX": borderPctX,
      "borderPctY": borderPctY,
      "cornerMarker": cornerMarker
    });
  };

  Client.prototype.initializeTiledBoardArea = function(tileCountX, tileCountY, x1, y1, x2, y2, areaId) {
    if (x1 == null) {
      x1 = 0.0;
    }
    if (y1 == null) {
      y1 = 0.0;
    }
    if (x2 == null) {
      x2 = 1.0;
    }
    if (y2 == null) {
      y2 = 1.0;
    }
    if (areaId == null) {
      areaId = void 0;
    }
    if (areaId !== void 0) {
      return this.sendMessage("initializeTiledBoardArea", {
        "id": areaId,
        "tileCountX": tileCountX,
        "tileCountY": tileCountY,
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2
      });
    } else {
      return this.sendMessage("initializeTiledBoardArea", {
        "tileCountX": tileCountX,
        "tileCountY": tileCountY,
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2
      });
    }
  };

  Client.prototype.removeBoardAreas = function() {
    return this.sendMessage("removeBoardAreas", {});
  };

  Client.prototype.removeBoardArea = function(areaId) {
    return this.sendMessage("removeBoardArea", {
      "id": areaId
    });
  };

  Client.prototype.requestTiledObjectPosition = function(areaId, validPositions) {
    return this.sendMessage("requestBrickPosition", {
      "areaId": areaId,
      "validPositions": validPositions
    });
  };

  Client.prototype.reportBackWhenBrickFoundAtAnyOfPositions = function(areaId, validPositions, id, stableTime) {
    if (id == null) {
      id = void 0;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    if (id !== void 0) {
      return this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
        "areaId": areaId,
        "validPositions": validPositions,
        "stableTime": stableTime,
        "id": id
      });
    } else {
      return this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", {
        "areaId": areaId,
        "validPositions": validPositions,
        "stableTime": stableTime
      });
    }
  };

  Client.prototype.reportBackWhenBrickMovedToAnyOfPositions = function(areaId, initialPosition, validPositions, id, stableTime) {
    if (id == null) {
      id = void 0;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    if (id !== void 0) {
      return this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
        "areaId": areaId,
        "initialPosition": initialPosition,
        "validPositions": validPositions,
        "stableTime": stableTime,
        "id": id
      });
    } else {
      return this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", {
        "areaId": areaId,
        "initialPosition": initialPosition,
        "validPositions": validPositions,
        "stableTime": stableTime
      });
    }
  };

  Client.prototype.reportBackWhenBrickMovedToPosition = function(areaId, position, validPositions, id, stableTime) {
    if (id == null) {
      id = void 0;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    if (id !== void 0) {
      return this.sendMessage("reportBackWhenBrickMovedToPosition", {
        "areaId": areaId,
        "position": position,
        "validPositions": validPositions,
        "stableTime": stableTime,
        "id": id
      });
    } else {
      return this.sendMessage("reportBackWhenBrickMovedToPosition", {
        "areaId": areaId,
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
