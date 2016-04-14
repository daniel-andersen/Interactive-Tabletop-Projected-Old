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

  Client.prototype.reset = function() {
    var message;
    message = {
      action: "reset",
      payload: {}
    };
    return this.socket.send(JSON.stringify(message));
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

  Client.prototype.requestTiledObjectPosition = function(validLocations) {
    return this.sendMessage("requestTiledObjectPosition", {
      "validLocations": validLocations
    });
  };

  Client.prototype.reportBackWhenTileAtAnyOfPositions = function(validLocations, id) {
    if (id == null) {
      id = null;
    }
    if (id !== null) {
      return this.sendMessage("reportBackWhenTileAtAnyOfPositions", {
        "validLocations": validLocations,
        "id": id
      });
    } else {
      return this.sendMessage("reportBackWhenTileAtAnyOfPositions", {
        "validLocations": validLocations
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
