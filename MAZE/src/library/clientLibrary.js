var ClientLibrary;

ClientLibrary = (function() {
  var action, borderPctX, borderPctY, cornerMarker, payload, socket;

  socket = null;

  action = "action";

  payload = "payload";

  function ClientLibrary(port1) {
    this.port = port1 != null ? port1 : 8080;
  }

  ClientLibrary.prototype.connect = function() {
    disconnect();
    return socket = new WebSocket("http://localhost:" + port + "");
  };

  ClientLibrary.prototype.disconnect = function() {
    if (socket) {
      socket.close();
      return socket = null;
    }
  };

  initializeTiledBoard(tileCountX, tileCountY, borderPctX = 0.0, borderPctY = 0.0, cornerMarker = "DEFAULT")(function() {
    var message;
    return message = {
      action: "initializeTiledBoard",
      payload: {
        "tileCountX": tileCountX,
        "tileCountY": tileCountY,
        "borderPctX": borderPctX,
        "borderPctY": borderPctY,
        "cornerMarker": cornerMarker
      }
    };
  });

  requestTiledObjectPosition(validLocations)(function() {
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
  });

  return ClientLibrary;

})();

//# sourceMappingURL=clientLibrary.js.map
