var Player, PlayerState, playerDefaultReachDistance, playerPlacementReachDistance;

PlayerState = {
  DISABLED: 0,
  INITIAL_PLACEMENT: 1,
  IDLE: 2,
  TURN: 3
};

playerPlacementReachDistance = 1;

playerDefaultReachDistance = 4;

Player = (function() {
  function Player(index) {
    this.state = PlayerState.INITIAL_PLACEMENT;
    this.reachDistance = playerPlacementReachDistance;
    this.position = new Position();
    this.index = index;
  }

  return Player;

})();

//# sourceMappingURL=player.js.map
