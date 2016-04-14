var Player, PlayerState, playerDefaultReachDistance, playerPlacementReachDistance;

PlayerState = {
  DISABLED: 0,
  INITIAL_PLACEMENT: 1,
  IDLE: 2,
  MOVING: 3
};

playerPlacementReachDistance = 3;

playerDefaultReachDistance = 4;

Player = (function() {
  function Player() {
    this.state = PlayerState.INITIAL_PLACEMENT;
    this.reachDistance = playerPlacementReachDistance;
    this.position = new Position();
  }

  return Player;

})();

//# sourceMappingURL=player.js.map
