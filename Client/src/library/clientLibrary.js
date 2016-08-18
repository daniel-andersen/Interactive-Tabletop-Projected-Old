var Client;

Client = (function() {
  function Client(port) {
    this.port = port != null ? port : 9001;
    this.debug_textField = null;
    this.debug_log = [];
    this.socket = void 0;
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
    if (this.socket != null) {
      this.socket.close();
      return this.socket = void 0;
    }
  };

  Client.prototype.enableDebug = function() {
    return this.sendMessage("enableDebug", {});
  };

  Client.prototype.reset = function(resolution) {
    var json;
    if (resolution == null) {
      resolution = void 0;
    }
    json = {};
    if (resolution != null) {
      json["resolution"] = resolution;
    }
    return this.sendMessage("reset", json);
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
    var json;
    if (filename == null) {
      filename = void 0;
    }
    json = {};
    if (filename != null) {
      json["filename"] = filename;
    }
    return this.sendMessage("takeScreenshot", json);
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

  Client.prototype.initializeBoardArea = function(x1, y1, x2, y2, areaId) {
    var json;
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
    json = {
      "x1": x1,
      "y1": y1,
      "x2": x2,
      "y2": y2
    };
    if (areaId != null) {
      json["id"] = areaId;
    }
    return this.sendMessage("initializeBoardArea", json);
  };

  Client.prototype.initializeTiledBoardArea = function(tileCountX, tileCountY, x1, y1, x2, y2, areaId) {
    var json;
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
    json = {
      "tileCountX": tileCountX,
      "tileCountY": tileCountY,
      "x1": x1,
      "y1": y1,
      "x2": x2,
      "y2": y2
    };
    if (areaId != null) {
      json["id"] = areaId;
    }
    return this.sendMessage("initializeTiledBoardArea", json);
  };

  Client.prototype.removeBoardAreas = function() {
    return this.sendMessage("removeBoardAreas", {});
  };

  Client.prototype.removeBoardArea = function(areaId) {
    return this.sendMessage("removeBoardArea", {
      "id": areaId
    });
  };

  Client.prototype.removeMarkers = function() {
    return this.sendMessage("removeMarkers", {});
  };

  Client.prototype.removeMarker = function(markerId) {
    return this.sendMessage("removeMarker", {
      "id": markerId
    });
  };

  Client.prototype.requestTiledObjectPosition = function(areaId, validPositions) {
    return this.sendMessage("requestBrickPosition", {
      "areaId": areaId,
      "validPositions": validPositions
    });
  };

  Client.prototype.reportBackWhenBrickFoundAtAnyOfPositions = function(areaId, validPositions, id, stableTime) {
    var json;
    if (id == null) {
      id = void 0;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    json = {
      "areaId": areaId,
      "validPositions": validPositions,
      "stableTime": stableTime
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", json);
  };

  Client.prototype.reportBackWhenBrickMovedToAnyOfPositions = function(areaId, initialPosition, validPositions, id, stableTime) {
    var json;
    if (id == null) {
      id = void 0;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    json = {
      "areaId": areaId,
      "initialPosition": initialPosition,
      "validPositions": validPositions,
      "stableTime": stableTime
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", json);
  };

  Client.prototype.reportBackWhenBrickMovedToPosition = function(areaId, position, validPositions, id, stableTime) {
    var json;
    if (id == null) {
      id = void 0;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    json = {
      "areaId": areaId,
      "position": position,
      "validPositions": validPositions,
      "stableTime": stableTime
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("reportBackWhenBrickMovedToPosition", json);
  };

  Client.prototype.initializeImageMarker = function(markerId, image) {
    return this.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        return _this.sendMessage("initializeImageMarker", {
          "markerId": markerId,
          "imageBase64": base64Image
        });
      };
    })(this));
  };

  Client.prototype.initializeShapeMarkerWithContour = function(markerId, contour) {
    return this.sendMessage("initializeShapeMarker", {
      "markerId": markerId,
      "shape": contour
    });
  };

  Client.prototype.initializeShapeMarkerWithImage = function(markerId, image) {
    return this.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        return _this.sendMessage("initializeShapeMarker", {
          "markerId": markerId,
          "imageBase64": base64Image
        });
      };
    })(this));
  };

  Client.prototype.reportBackWhenMarkerFound = function(areaId, markerId, id, stableTime, sleepTime) {
    var json;
    if (id == null) {
      id = void 0;
    }
    if (stableTime == null) {
      stableTime = 1.5;
    }
    if (sleepTime == null) {
      sleepTime = 1.0;
    }
    json = {
      "areaId": areaId,
      "markerId": markerId,
      "stableTime": stableTime,
      "sleepTime": sleepTime
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("reportBackWhenMarkerFound", json);
  };

  Client.prototype.requestMarkers = function(areaId, markerId, stableTime) {
    if (stableTime == null) {
      stableTime = 1.5;
    }
    return this.sendMessage("requestMarkers", {
      "areaId": areaId,
      "markerId": markerId,
      "stableTime": stableTime
    });
  };

  Client.prototype.sendMessage = function(action, payload) {
    var message;
    message = {
      "action": action,
      "payload": payload
    };
    return this.socket.send(JSON.stringify(message));
  };

  Client.prototype.convertImageToDataURL = function(image, callback) {
    var canvas, ctx, dataURL;
    canvas = document.createElement("CANVAS");
    canvas.width = image.width;
    canvas.height = image.height;
    ctx = canvas.getContext("2d");
    ctx.drawImage(image, 0, 0);
    dataURL = canvas.toDataURL("image/png");
    dataURL = dataURL.replace(/^data:image\/png;base64,/, "");
    callback(dataURL);
    return canvas = null;
  };

  return Client;

})();

//# sourceMappingURL=clientLibrary.js.map
