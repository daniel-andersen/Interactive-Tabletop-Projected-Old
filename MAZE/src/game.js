/**
* The core TemplateGame game file.
*
* This file is only used to initalise (start-up) the main Kiwi Game
* and add all of the relevant states to that Game.
*/

// Initialise the Kiwi Game.

var gameOptions = {
	renderer: Kiwi.RENDERER_CANVAS,
	width: 1280,
	height: 800
};

var game = new Kiwi.Game( "content", "MAZE", null, gameOptions );

// Add all the States we are going to use.
game.states.addState( MAZE.Loading );
game.states.addState( MAZE.Intro );
game.states.addState( MAZE.Play );

game.states.switchState( "Loading" );
