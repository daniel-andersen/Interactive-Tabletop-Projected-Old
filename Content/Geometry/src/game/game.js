var GEOMETRY, GeometryGame, GeometryType, geometryGame;

GEOMETRY = GEOMETRY || {};

GEOMETRY.Game = new Kiwi.State("Game");

geometryGame = null;

GEOMETRY.Game.preload = function() {
  return this.addImage("corners", "assets/img/game/corners.png");
};

GEOMETRY.Game.create = function() {
  Kiwi.State.prototype.create.call(this);
  geometryGame = new GeometryGame(this);
  return geometryGame.start();
};

GEOMETRY.Game.shutDown = function() {
  Kiwi.State.prototype.shutDown.call(this);
  return geometryGame.stop();
};

GEOMETRY.Game.update = function() {
  Kiwi.State.prototype.update.call(this);
  return geometryGame.update();
};

GeometryType = {
  TRIANGLE: 0,
  SQUARE: 1,
  CIRCLE: 2,
  OTHER: 3
};

GeometryGame = (function() {
  function GeometryGame(kiwiState) {
    this.kiwiState = kiwiState;
    this.client = new Client();
  }

  GeometryGame.prototype.start = function() {
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

  GeometryGame.prototype.stop = function() {
    return this.client.disconnect();
  };

  GeometryGame.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.initializeBoard();
      };
    })(this));
  };

  GeometryGame.prototype.onMessage = function(json) {};

  GeometryGame.prototype.update = function() {};

  GeometryGame.prototype.setup = function() {
    this.boardCentimeterScale = 85.0;
    this.verticalAspectScale = this.kiwiState.game.stage.height / this.kiwiState.game.stage.width;
    this.geometry = [];
    this.geometryRelaxationTime = 1.0;
    return this.geometryUpdateMinMoveDistance = 0.01;
  };

  GeometryGame.prototype.setupUi = function() {
    var content;
    content = document.getElementById("content");
    content.style.visibility = "visible";
    this.corners = new Kiwi.GameObjects.StaticImage(this.kiwiState, this.kiwiState.textures.corners, 0, 0);
    return this.kiwiState.addChild(this.corners);
  };

  GeometryGame.prototype.initializeBoard = function() {
    return this.client.initializeBoard(void 0, void 0, (function(_this) {
      return function(action, payload) {
        return _this.initializeBoardAreas();
      };
    })(this));
  };

  GeometryGame.prototype.initializeBoardAreas = function() {
    this.wholeBoardAreaId = 0;
    return this.client.initializeBoardArea(0.0, 0.0, 1.0, 1.0, this.wholeBoardAreaId, (function(_this) {
      return function(action, payload) {
        return _this.startNewGame();
      };
    })(this));
  };

  GeometryGame.prototype.startNewGame = function() {
    return setTimeout((function(_this) {
      return function() {
        return _this.findContours();
      };
    })(this), 2000);
  };

  GeometryGame.prototype.findContours = function() {
    return this.client.requestContours(this.wholeBoardAreaId, 0.04, void 0, (function(_this) {
      return function(action, payload) {
        _this.foundContours(payload);
        return _this.findContours();
      };
    })(this));
  };

  GeometryGame.prototype.foundContours = function(payload) {
    var geometryInfo, j, len, ref;
    ref = this.geometry.slice();
    for (j = 0, len = ref.length; j < len; j++) {
      geometryInfo = ref[j];
      while (geometryInfo["history"].length > 0 && geometryInfo["history"][0] < Util.currentTimeSeconds() - this.geometryRelaxationTime) {
        geometryInfo["history"].shift();
      }
      if (geometryInfo["history"].length === 0) {
        this.removeGeometryUi(geometryInfo);
        this.geometry.splice(this.geometry.indexOf(geometryInfo), 1);
      }
    }
    return this.updateGeometry(payload["contours"], payload["hierarchy"]);
  };

  GeometryGame.prototype.updateGeometryUi = function(geometryInfo) {
    console.log("Updating UI for geometry of type " + this.contourType(geometryInfo["contourDict"]));
    this.removeGeometryUi(geometryInfo);
    switch (geometryInfo["type"]) {
      case GeometryType.TRIANGLE:
        return this.updateTriangleShapeUi(geometryInfo);
      case GeometryType.SQUARE:
        return this.updateSquareShapeUi(geometryInfo);
    }
  };

  GeometryGame.prototype.updateTriangleShapeUi = function(geometryInfo) {
    this.updateSideLengthsUi(geometryInfo);
    return this.updateAreaUi(geometryInfo);
  };

  GeometryGame.prototype.updateSquareShapeUi = function(geometryInfo) {
    this.updateSideLengthsUi(geometryInfo);
    return this.updateAreaUi(geometryInfo);
  };

  GeometryGame.prototype.updateSideLengthsUi = function(geometryInfo) {
    var center, contour, contourDict, element, index, index1, index2, j, length, p, p1, p2, ref, results, scaledContour, text;
    contourDict = geometryInfo["contourDict"];
    contour = contourDict["contour"];
    scaledContour = this.aspectScaledContour(contour);
    results = [];
    for (index = j = 0, ref = contour.length - 1; 0 <= ref ? j <= ref : j >= ref; index = 0 <= ref ? ++j : --j) {
      index1 = index;
      index2 = (index + 1) % contour.length;
      center = this.contourCenter(contourDict);
      center = [center[0] * this.kiwiState.game.stage.width, center[1] * this.kiwiState.game.stage.height];
      p1 = contour[index];
      p2 = contour[(index + 1) % contour.length];
      p = [((p1[0] + p2[0]) / 2.0) * this.kiwiState.game.stage.width, ((p1[1] + p2[1]) / 2.0) * this.kiwiState.game.stage.height];
      p = this.translateAwayFromCenter(p, center);
      length = this.pointsDistance(scaledContour[index1], scaledContour[index2]) * this.boardCentimeterScale;
      text = new Kiwi.GameObjects.Textfield(this.kiwiState, length.toFixed(0), p[0], p[1], "#FF0000", 12);
      text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER;
      element = this.kiwiState.addChild(text);
      geometryInfo["uiElements"]["line" + index] = element;
      text = new Kiwi.GameObjects.Textfield(this.kiwiState, "cm", p[0], p[1] + 12, "#FF0000", 12);
      text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER;
      element = this.kiwiState.addChild(text);
      results.push(geometryInfo["uiElements"]["line" + index + "_cm"] = element);
    }
    return results;
  };

  GeometryGame.prototype.updateAreaUi = function(geometryInfo) {
    var area, center, contourDict, element, text;
    contourDict = geometryInfo["contourDict"];
    center = this.contourCenter(contourDict);
    center = [center[0] * this.kiwiState.game.stage.width, center[1] * this.kiwiState.game.stage.height];
    area = contourDict["area"] * (this.boardCentimeterScale * this.verticalAspectScale) * this.boardCentimeterScale;
    text = new Kiwi.GameObjects.Textfield(this.kiwiState, area.toFixed(0), center[0], center[1], "#00FF00", 12);
    text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER;
    element = this.kiwiState.addChild(text);
    geometryInfo["uiElements"]["area"] = element;
    text = new Kiwi.GameObjects.Textfield(this.kiwiState, "cm2", center[0], center[1] + 12, "#00FF00", 12);
    text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER;
    element = this.kiwiState.addChild(text);
    return geometryInfo["uiElements"]["area_cm2"] = element;
  };

  GeometryGame.prototype.removeGeometryUi = function(geometryInfo) {
    var element, name, ref;
    ref = geometryInfo["uiElements"];
    for (name in ref) {
      element = ref[name];
      element.destroy();
      console.log("Removing element: " + element);
    }
    return geometryInfo["uiElements"] = {};
  };

  GeometryGame.prototype.aspectScaledContour = function(contour) {
    var p;
    return (function() {
      var j, len, results;
      results = [];
      for (j = 0, len = contour.length; j < len; j++) {
        p = contour[j];
        results.push([p[0], p[1] * this.verticalAspectScale]);
      }
      return results;
    }).call(this);
  };

  GeometryGame.prototype.updateGeometry = function(contours, hierarchy) {
    var contourDict, currentContourDict, geometryInfo, i, index, j, k, l, len, len1, len2, len3, m, matchedContourDict, matchedContourIndices, n, o, q, ref, ref1, ref2, ref3, ref4, ref5, ref6, results;
    ref = this.geometry;
    for (j = 0, len = ref.length; j < len; j++) {
      geometryInfo = ref[j];
      geometryInfo["matchedContourIndex"] = -1;
    }
    matchedContourIndices = (function() {
      var k, ref1, results;
      results = [];
      for (i = k = 0, ref1 = contours.length - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; i = 0 <= ref1 ? ++k : --k) {
        results.push(-1);
      }
      return results;
    })();
    for (index = k = 0, ref1 = contours.length - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; index = 0 <= ref1 ? ++k : --k) {
      if (!this.isValidContour(contours, hierarchy, index)) {
        continue;
      }
      contourDict = contours[index];
      ref2 = this.geometry;
      for (l = 0, len1 = ref2.length; l < len1; l++) {
        geometryInfo = ref2[l];
        if (geometryInfo["matchedContourIndex"] === -1 && this.isSameShape(contourDict, geometryInfo["contourDict"]) && this.isSamePosition(contourDict, geometryInfo["contourDict"])) {
          geometryInfo["matchedContourIndex"] = index;
          matchedContourIndices[index] = geometryInfo["id"];
          break;
        }
      }
    }
    for (index = m = 0, ref3 = contours.length - 1; 0 <= ref3 ? m <= ref3 : m >= ref3; index = 0 <= ref3 ? ++m : --m) {
      if (!this.isValidContour(contours, hierarchy, index)) {
        continue;
      }
      contourDict = contours[index];
      ref4 = this.geometry;
      for (n = 0, len2 = ref4.length; n < len2; n++) {
        geometryInfo = ref4[n];
        if (geometryInfo["matchedContourIndex"] === -1 && this.isSameShape(contourDict, geometryInfo["contourDict"])) {
          geometryInfo["matchedContourIndex"] = index;
          matchedContourIndices[index] = geometryInfo["id"];
          break;
        }
      }
    }
    for (index = o = 0, ref5 = contours.length - 1; 0 <= ref5 ? o <= ref5 : o >= ref5; index = 0 <= ref5 ? ++o : --o) {
      if (matchedContourIndices[index] === -1) {
        contourDict = contours[index];
        if (this.isValidContour(contours, hierarchy, index)) {
          geometryInfo = this.newGeometry(contourDict, hierarchy);
          geometryInfo["matchedContourIndex"] = index;
          matchedContourIndices[index] = geometryInfo["id"];
          console.log("Added new geometry of type: " + this.contourType(contourDict));
        }
      }
    }
    ref6 = this.geometry;
    results = [];
    for (q = 0, len3 = ref6.length; q < len3; q++) {
      geometryInfo = ref6[q];
      if (geometryInfo["matchedContourIndex"] === -1) {
        continue;
      }
      matchedContourDict = contours[geometryInfo["matchedContourIndex"]];
      currentContourDict = geometryInfo["contourDict"];
      geometryInfo["history"].push(Util.currentTimeSeconds());
      this.updateGeometryInfo(geometryInfo, matchedContourDict);
      if (this.shouldUpdateGeometryUi(geometryInfo, currentContourDict, matchedContourDict)) {
        results.push(this.updateGeometryUi(geometryInfo));
      } else {
        results.push(void 0);
      }
    }
    return results;
  };

  GeometryGame.prototype.updateGeometryInfo = function(geometryInfo, contourDict) {
    return geometryInfo["contourDict"] = contourDict;
  };

  GeometryGame.prototype.newGeometry = function(contourDict, hierarchy) {
    var geometryInfo;
    geometryInfo = {
      "id": Util.randomInRange(0, 100000),
      "contourDict": contourDict,
      "hierarchy": hierarchy,
      "type": this.contourType(contourDict),
      "history": [],
      "uiElements": {}
    };
    this.geometry.push(geometryInfo);
    return geometryInfo;
  };

  GeometryGame.prototype.isSameShape = function(contourDict1, contourDict2) {
    var arcLengthRatio, areaRatio, contour1, contour2;
    contour1 = contourDict1["contour"];
    contour2 = contourDict2["contour"];
    if (this.contourType(contourDict1) !== this.contourType(contourDict2)) {
      return false;
    }
    arcLengthRatio = Math.max(contour1["arclength"], contour2["arclength"]) / Math.min(contour1["arclength"], contour2["arclength"]);
    if (arcLengthRatio > 1.1) {
      return false;
    }
    areaRatio = Math.max(contour1["area"], contour2["area"]) / Math.min(contour1["area"], contour2["area"]);
    if (areaRatio > 1.1) {
      return false;
    }
    return true;
  };

  GeometryGame.prototype.isSamePosition = function(contourDict1, contourDict2) {
    return this.contourDistance(contourDict1, contourDict2) < 0.05;
  };

  GeometryGame.prototype.shouldUpdateGeometryUi = function(geometryInfo, currentContourDict, newContourDict) {
    var currentContour, index, j, k, matchIndex, matchLeft, matchRight, newContour, p1, p2, ref, ref1;
    newContour = newContourDict["contour"];
    currentContour = currentContourDict["contour"];
    if (Object.keys(geometryInfo["uiElements"]).length === 0) {
      return true;
    }
    matchIndex = void 0;
    p1 = currentContour[0];
    for (index = j = 0, ref = newContour.length - 1; 0 <= ref ? j <= ref : j >= ref; index = 0 <= ref ? ++j : --j) {
      p2 = newContour[index];
      if (this.pointsDistance(p1, p2) < this.geometryUpdateMinMoveDistance) {
        matchIndex = index;
      }
    }
    if (matchIndex == null) {
      return true;
    }
    matchLeft = true;
    matchRight = true;
    for (index = k = 0, ref1 = currentContour.length - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; index = 0 <= ref1 ? ++k : --k) {
      p1 = currentContour[index];
      p2 = newContour[(matchIndex + index) % newContour.length];
      if (this.pointsDistance(p1, p2) >= this.geometryUpdateMinMoveDistance) {
        matchRight = false;
      }
      p2 = newContour[(matchIndex - index + newContour.length) % newContour.length];
      if (this.pointsDistance(p1, p2) >= this.geometryUpdateMinMoveDistance) {
        matchLeft = false;
      }
    }
    return !matchLeft && !matchRight;
  };

  GeometryGame.prototype.contourDistance = function(contourDict1, contourDict2) {
    var center1, center2;
    center1 = this.contourCenter(contourDict1);
    center2 = this.contourCenter(contourDict2);
    return this.pointsDistance(center1, center2);
  };

  GeometryGame.prototype.pointsDistance = function(p1, p2) {
    var deltaX, deltaY;
    deltaX = p1[0] - p2[0];
    deltaY = p1[1] - p2[1];
    return Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  };

  GeometryGame.prototype.isValidContour = function(contours, hierarchy, index) {
    var childIndex, contourDict;
    contourDict = contours[index];
    if (this.contourType(contourDict) === GeometryType.OTHER) {
      return false;
    }
    if (contourDict["area"] < 0.001) {
      return false;
    }
    if (contourDict["area"] > 0.9) {
      return false;
    }
    childIndex = hierarchy[index][2];
    if (childIndex !== -1) {
      return false;
    }
    return true;
  };

  GeometryGame.prototype.contourType = function(contourDict) {
    if (contourDict["contour"].length === 3) {
      return GeometryType.TRIANGLE;
    }
    if (contourDict["contour"].length === 4) {
      return GeometryType.SQUARE;
    }
    return GeometryType.OTHER;
  };

  GeometryGame.prototype.contourCenter = function(contourDict) {
    var center, contour, j, len, p;
    contour = contourDict["contour"];
    center = [0.0, 0.0];
    for (j = 0, len = contour.length; j < len; j++) {
      p = contour[j];
      center[0] += p[0];
      center[1] += p[1];
    }
    center[0] /= contour.length;
    center[1] /= contour.length;
    return center;
  };

  GeometryGame.prototype.translateAwayFromCenter = function(p, center) {
    var delta, distance, unit;
    distance = this.pointsDistance(p, center);
    if (distance === 0) {
      return p;
    }
    delta = [p[0] - center[0], p[1] - center[1]];
    unit = [delta[0] / distance, delta[1] / distance];
    return [center[0] + (unit[0] * (distance + 50)), center[1] + (unit[1] * (distance + 50))];
  };

  return GeometryGame;

})();

//# sourceMappingURL=game.js.map
