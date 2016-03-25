var Client;

Client = (function() {
  var action, payload, socket;

  socket = null;

  action = "action";

  payload = "payload";

  function Client(port) {
    this.port = port != null ? port : 9001;
    this.socketOpen = false;
  }

  Client.prototype.connect = function(onSocketOpen) {
    this.disconnect();
    this.socket = new WebSocket("ws://localhost:" + this.port + "/");
    this.socket.onopen = (function(_this) {
      return function(event) {
        return onSocketOpen();
      };
    })(this);
    return this.socket.onmessage = (function(_this) {
      return function(event) {
        return _this.handleMessage(event.data);
      };
    })(this);
  };

  Client.prototype.disconnect = function() {
    if (this.socket) {
      this.socket.close();
      return this.socket = null;
    }
  };

  Client.prototype.handleMessage = function(message) {
    return alert(message);
  };

  Client.prototype.initializeTiledBoard = function(tileCountX, tileCountY, borderPctX, borderPctY, cornerMarker) {
    var message;
    if (borderPctX == null) {
      borderPctX = 0.0;
    }
    if (borderPctY == null) {
      borderPctY = 0.0;
    }
    if (cornerMarker == null) {
      cornerMarker = "DEFAULT";
    }
    message = {
      action: "initializeTiledBoard",
      payload: {
        "tileCountX": tileCountX,
        "tileCountY": tileCountY,
        "borderPctX": borderPctX,
        "borderPctY": borderPctY,
        "cornerMarker": cornerMarker
      }
    };
    return this.socket.send(JSON.stringify(message));
  };

  Client.prototype.requestTiledObjectPosition = function(validLocations) {
    var location, message;
    return message = {
      action: "requestTiledObjectPosition",
      payload: {
        "validLocations": [
          (function() {
            var i, len, results;
            results = [];
            for (i = 0, len = validLocations.length; i < len; i++) {
              location = validLocations[i];
              results.push([location.x, location.y]);
            }
            return results;
          })()
        ]
      }
    };
  };

  return Client;

})();

//# sourceMappingURL=clientLibrary.js.map
