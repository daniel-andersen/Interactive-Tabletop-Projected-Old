MAZE = MAZE or {}
MAZE.Game = new Kiwi.State("Game")

tileLayers = []

maze = null

MAZE.Game.preload = ->
    @addJSON("tilemap", "assets/maps/sample.json")
    @addSpriteSheet("tiles", "assets/img/tiles/board_tiles.png", 40, 40)
    @addImage("logo", "assets/img/menu/title.png")

MAZE.Game.create = ->
    Kiwi.State::create.call(this)

    maze = new Maze(this)
    maze.start()

MAZE.Game.shutDown = ->
    Kiwi.State::shutDown.call(this)
    maze.stop()

MAZE.Game.update = ->
    Kiwi.State::update.call(this)
