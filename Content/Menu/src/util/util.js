var Position, Util;

Util = (function() {
  function Util() {}

  Util.randomInRange = function(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
  };

  Util.currentTimeSeconds = function() {
    return new Date().getTime() / 1000.0;
  };

  Util.angleDifference = function(angle1, angle2) {
    return (((angle1 - angle2) + Math.PI) % (Math.PI * 2.0)) - Math.PI;
  };

  Util.fadeInElement = function(element, duration, kiwiState, delay, onCompleteCallback) {
    var tween;
    if (delay == null) {
      delay = 0;
    }
    if (onCompleteCallback == null) {
      onCompleteCallback = void 0;
    }
    element.alpha = 0.0;
    element.visible = true;
    tween = kiwiState.game.tweens.create(element);
    tween.delay(delay);
    if (onCompleteCallback != null) {
      tween.onComplete((function(_this) {
        return function(a, b) {
          return onCompleteCallback();
        };
      })(this));
    }
    return tween.to({
      alpha: 1.0
    }, duration, Kiwi.Animations.Tweens.Easing.Linear.In, true);
  };

  Util.fadeOutElement = function(element, duration, kiwiState, onCompleteCallback) {
    var tween;
    if (onCompleteCallback == null) {
      onCompleteCallback = void 0;
    }
    tween = kiwiState.game.tweens.create(element);
    tween.onComplete((function(_this) {
      return function(a, b) {
        element.visible = false;
        if (onCompleteCallback != null) {
          return onCompleteCallback();
        }
      };
    })(this));
    return tween.to({
      alpha: 0.0
    }, duration, Kiwi.Animations.Tweens.Easing.Linear.In, true);
  };

  Util.centerElement = function(element, kiwiState) {
    element.x = (kiwiState.game.stage.width - element.width) / 2.0;
    return element.y = (kiwiState.game.stage.height - element.height) / 2.0;
  };

  Util.positionElement = function(element, x, y, kiwiState) {
    element.x = (kiwiState.game.stage.width * x) - (element.width / 2.0);
    return element.y = (kiwiState.game.stage.height * y) - (element.height / 2.0);
  };

  return Util;

})();

Position = (function() {
  function Position(x1, y1) {
    this.x = x1 != null ? x1 : 0;
    this.y = y1 != null ? y1 : 0;
  }

  Position.prototype.equals = function(position) {
    return this.x === position.x && this.y === position.y;
  };

  return Position;

})();

//# sourceMappingURL=util.js.map
