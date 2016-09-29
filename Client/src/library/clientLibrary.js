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

  "connect: Establishes a websocket connection to the server.\n\nTakes two callback parameters.\nonSocketOpen: onSocketOpen() is called when socket connection has been established.\nonMessage: onMessage(json) is called with json response from server. The json consists of the following mandatory fields:\n  - result: Fx. \"OK\" or \"BOARD_NOT_RECOGNIZED\"\n  - action: Action which message is a reply to, fx. \"reset\" or \"initializeBoard\"\n  - payload: The actual payload. Varies from response to response.\n  - requestId: Unique request id for which this is a response to.";

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

  "disconnect: Disconnects from the server.";

  Client.prototype.disconnect = function() {
    if (this.socket != null) {
      this.socket.close();
      return this.socket = void 0;
    }
  };

  "enableDebug: Enables server debug.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "reset: Resets the server.\n\nresolution: (Optional) Camera resolution to use in form [width, height].\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "resetReporters: Resets all active reporters.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "resetReporter: Resets a specific reporter.\n\nreporterId: Reporter ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "takeScreenshot: Takes and stores a screenshot from the camera.\n\nfilename: (Optional) Screenshot filename.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "initializeBoard: Initializes the board.\n\nborderPercentage: (Optional) Border percentage [width (0..1), height (0..1)] in percentage of width and height.\ncornerMarker: (Optional) Corner marker to use.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeBoard = function(borderPercentage, cornerMarker, completionCallback) {
    var json, requestId;
    if (borderPercentage == null) {
      borderPercentage = void 0;
    }
    if (cornerMarker == null) {
      cornerMarker = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId
    };
    if (borderPercentage != null) {
      json["borderPercentage"] = borderPercentage;
    }
    if (cornerMarker != null) {
      json["cornerMarker"] = cornerMarker;
    }
    return this.sendMessage("initializeBoard", json);
  };

  "initializeBoardArea: Initializes an area of the board. Is used to search for markers in a specific region, etc.\n\nx1: Left coordinate in percentage [0..1] of board width.\ny1: Top in percentage [0..1] of board height.\nx2: Right coordinate in percentage [0..1] of board width.\ny2: Bottom coordinate in percentage [0..1] of board height.\nareaId: (Optional) Area ID to use. If none is given, a random area ID is generated and returned from the server.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "initializeTiledBoardArea: Initializes a tiled board area, ie. an area which is divided into equally sized tiles.\n\ntileCountX: Number of tiles horizontally.\ntileCountY: Number of tiles vertically.\nx1: Left coordinate in percentage [0..1] of board width.\ny1: Top in percentage [0..1] of board height.\nx2: Right coordinate in percentage [0..1] of board width.\ny2: Bottom coordinate in percentage [0..1] of board height.\nareaId: (Optional) Area ID to use. If none is given, a random area ID is generated and returned from the server.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "removeBoardAreas: Removes all board areas at server end. Maintaining a board area requires some server processing, so\nit is good practice to remove them when not used any longer.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "removeBoardArea: Removes a specific board area at server end. Maintaining a board area requires some server processing, so\nit is good practice to remove them when not used any longer.\n\nareaId: Board area ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "removeMarkers: Removes all markers from the server.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "removeMarker: Removes a specific marker from the server.\n\nmarkerId: Marker ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "requestTiledBrickPosition: Returns the position of a brick among the given possible positions in a tiled area.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.requestTiledBrickPosition = function(areaId, validPositions, completionCallback) {
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

  "reportBackWhenBrickFoundAtAnyOfPositions: Keeps searching for a brick in the given positions in a tiled area and returns\nthe position when found.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "reportBackWhenBrickMovedToAnyOfPositions: Reports back when brick has moved to any of the given positions in a tiled area.\n\nareaId: Area ID of tiled board area.\ninitialPosition: Position where brick is currently located in form [x, y].\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "reportBackWhenBrickMovedToPosition: Reports back when brick has moved to the given position in a tiled area.\n\nposition: Target position to trigger the callback in form [x, y].\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...] where the brick could be located.\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "initializeImageMarker: Initializes an image marker.\n\nmarkerId: Marker ID.\nimage: Source marker image.\nminMatches: (Optional) Minimum number of matches required. (8 is recommended minimum).\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "initializeHaarClassifierMarker: Initializes a Haar Classifier with the given filename.\n\nmarkerId: Marker ID.\nfilename: Filename of Haar Classifier.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "initializeShapeMarkerWithContour: Initializes a shape marker with the given contour.\n\nmarkerId: Marker ID.\ncontour: Contour of shape in form [[x, y], [x, y], ...].\nminArea: (Optional) Minimum area in percentage [0..1] of board area image size.\nmaxArea: (Optional) Maximum area in percentage [0..1] of board area image size.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "initializeShapeMarkerWithImage: Initializes a shape marker with shape extracted from the given image.\n\nmarkerId: Marker ID.\nimage: Marker image. Must be black contour on white image.\nminArea: (Optional) Minimum area in percentage [0..1] of board area image size.\nmaxArea: (Optional) Maximum area in percentage [0..1] of board area image size.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "reportBackWhenMarkerFound: Keeps searching for marker and reports back when found.\n\nareaId: Area ID to search for marker in.\nmarkerId: Marker ID to search for.\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "requestMarkers: Returns which markers among the given list of markers that are currently visible in the given area.\n\nareaId: Area ID to search for markers in.\nmarkerIds: Marker IDs to search for in form [id, id, ...].\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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

  "startTrackingMarker: Continously tracks a marker in the given area. Continously reports back.\n\nareaId: Area ID to track marker in.\nmarkerId: Marker ID to track.\nid: (Optional) Reporter ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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
