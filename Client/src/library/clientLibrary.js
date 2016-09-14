var Client;

Client = (function() {
  function Client(port) {
    this.port = port != null ? port : 9001;
    this.debug_textField = null;
    this.debug_log = [];
    this.socket = void 0;
    this.socketOpen = false;
    this.requests = {};
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
        _this.performCompletionCallbackForRequest(json);
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

  Client.prototype.enableDebug = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("enableDebug", {
      "requestId": requestId
    });
  };

  Client.prototype.reset = function(resolution, completionCallback) {
    var json, requestId;
    if (resolution == null) {
      resolution = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    this.requests = {};
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId
    };
    if (resolution != null) {
      json["resolution"] = resolution;
    }
    return this.sendMessage("reset", json);
  };

  Client.prototype.resetReporters = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("resetReporters", {
      "requestId": requestId
    });
  };

  Client.prototype.resetReporter = function(reporterId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("resetReporter", {
      "requestId": requestId,
      "id": reporterId
    });
  };

  Client.prototype.takeScreenshot = function(filename, completionCallback) {
    var json, requestId;
    if (filename == null) {
      filename = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId
    };
    if (filename != null) {
      json["filename"] = filename;
    }
    return this.sendMessage("takeScreenshot", json);
  };

  Client.prototype.initializeBoard = function(borderPctX, borderPctY, cornerMarker, completionCallback) {
    var requestId;
    if (borderPctX == null) {
      borderPctX = 0.0;
    }
    if (borderPctY == null) {
      borderPctY = 0.0;
    }
    if (cornerMarker == null) {
      cornerMarker = "DEFAULT";
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("initializeBoard", {
      "requestId": requestId,
      "borderPctX": borderPctX,
      "borderPctY": borderPctY,
      "cornerMarker": cornerMarker
    });
  };

  Client.prototype.initializeBoardArea = function(x1, y1, x2, y2, areaId, completionCallback) {
    var json, requestId;
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
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
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

  Client.prototype.initializeTiledBoardArea = function(tileCountX, tileCountY, x1, y1, x2, y2, areaId, completionCallback) {
    var json, requestId;
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
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
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

  Client.prototype.removeBoardAreas = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeBoardAreas", {
      "requestId": requestId
    });
  };

  Client.prototype.removeBoardArea = function(areaId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeBoardArea", {
      "requestId": requestId,
      "id": areaId
    });
  };

  Client.prototype.removeMarkers = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeMarkers", {
      "requestId": requestId
    });
  };

  Client.prototype.removeMarker = function(markerId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeMarker", {
      "requestId": requestId,
      "id": markerId
    });
  };

  Client.prototype.requestTiledObjectPosition = function(areaId, validPositions, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("requestBrickPosition", {
      "requestId": requestId,
      "areaId": areaId,
      "validPositions": validPositions
    });
  };

  Client.prototype.reportBackWhenBrickFoundAtAnyOfPositions = function(areaId, validPositions, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "validPositions": validPositions
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", json);
  };

  Client.prototype.reportBackWhenBrickMovedToAnyOfPositions = function(areaId, initialPosition, validPositions, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "initialPosition": initialPosition,
      "validPositions": validPositions
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", json);
  };

  Client.prototype.reportBackWhenBrickMovedToPosition = function(areaId, position, validPositions, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "position": position,
      "validPositions": validPositions
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenBrickMovedToPosition", json);
  };

  Client.prototype.initializeImageMarker = function(markerId, image, minMatches, completionCallback) {
    var requestId;
    if (minMatches == null) {
      minMatches = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        var json;
        json = {
          "requestId": requestId,
          "markerId": markerId,
          "imageBase64": base64Image
        };
        if (minMatches != null) {
          json["minMatches"] = minMatches;
        }
        return _this.sendMessage("initializeImageMarker", json);
      };
    })(this));
  };

  Client.prototype.initializeHaarClassifierMarker = function(markerId, filename, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.readFileBase64(filename, (function(_this) {
      return function(base64Data) {
        return _this.sendMessage("initializeHaarClassifierMarker", {
          "requestId": requestId,
          "markerId": markerId,
          "dataBase64": base64Data
        });
      };
    })(this));
  };

  Client.prototype.initializeShapeMarkerWithContour = function(markerId, contour, minArea, maxArea, completionCallback) {
    var json, requestId;
    if (minArea == null) {
      minArea = void 0;
    }
    if (maxArea == null) {
      maxArea = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "markerId": markerId,
      "shape": contour
    };
    if (minArea != null) {
      json["minArea"] = minArea;
    }
    if (maxArea != null) {
      json["maxArea"] = maxArea;
    }
    return this.sendMessage("initializeShapeMarker", json);
  };

  Client.prototype.initializeShapeMarkerWithImage = function(markerId, image, minArea, maxArea, completionCallback) {
    var requestId;
    if (minArea == null) {
      minArea = void 0;
    }
    if (maxArea == null) {
      maxArea = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        var json;
        json = {
          "requestId": requestId,
          "markerId": markerId,
          "imageBase64": base64Image
        };
        if (minArea != null) {
          json["minArea"] = minArea;
        }
        if (maxArea != null) {
          json["maxArea"] = maxArea;
        }
        return _this.sendMessage("initializeShapeMarker", json);
      };
    })(this));
  };

  Client.prototype.reportBackWhenMarkerFound = function(areaId, markerId, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "markerId": markerId
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenMarkerFound", json);
  };

  Client.prototype.requestMarkers = function(areaId, markerIds, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "markerIds": markerIds
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("requestMarkers", json);
  };

  Client.prototype.startTrackingMarker = function(areaId, markerId, id, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "markerId": markerId
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("startTrackingMarker", json);
  };

  Client.prototype.sendMessage = function(action, payload) {
    var message;
    message = {
      "action": action,
      "payload": payload
    };
    return this.socket.send(JSON.stringify(message));
  };

  Client.prototype.addCompletionCallback = function(completionCallback) {
    var requestId;
    if (completionCallback != null) {
      requestId = ClientUtil.randomRequestId();
      this.requests[requestId] = {
        "timestamp": Date.now(),
        "completionCallback": completionCallback
      };
      return requestId;
    } else {
      return void 0;
    }
  };

  Client.prototype.performCompletionCallbackForRequest = function(json) {
    var action, completionCallback, payload, requestDict, requestId, shouldRemoveRequest;
    action = json["action"];
    requestId = json["requestId"];
    payload = json["payload"];
    if ((action == null) || (requestId == null) || (payload == null)) {
      return;
    }
    requestDict = this.requests[requestId];
    if (requestDict == null) {
      return;
    }
    completionCallback = requestDict["completionCallback"];
    shouldRemoveRequest = completionCallback(action, payload);
    if ((shouldRemoveRequest == null) || shouldRemoveRequest) {
      return delete this.requests[requestId];
    }
  };

  Client.prototype.convertImageToDataURL = function(image, callback) {
    var canvas, ctx, dataURL;
    canvas = document.createElement("CANVAS");
    canvas.width = image.width;
    canvas.height = image.height;
    ctx = canvas.getContext("2d");
    ctx.drawImage(image, 0, 0);
    dataURL = canvas.toDataURL("image/png");
    dataURL = dataURL.replace(/^.*;base64,/, "");
    callback(dataURL);
    return canvas = null;
  };

  Client.prototype.readFileBase64 = function(filename, callback) {
    var xhr;
    xhr = new XMLHttpRequest();
    xhr.open("GET", filename, true);
    xhr.responseType = "blob";
    xhr.onload = function(e) {
      var blob, fileReader;
      if (this.status === 200) {
        blob = new Blob([this.response], {
          type: "text/xml"
        });
        fileReader = new FileReader();
        fileReader.onload = (function(_this) {
          return function(e) {
            var contents;
            contents = e.target.result;
            contents = contents.replace(/^.*;base64,/, "");
            return callback(contents);
          };
        })(this);
        fileReader.onerror = (function(_this) {
          return function(e) {
            return console.log("Error loading file: " + e);
          };
        })(this);
        return fileReader.readAsDataURL(blob);
      }
    };
    return xhr.send();
  };

  return Client;

})();

//# sourceMappingURL=clientLibrary.js.map
