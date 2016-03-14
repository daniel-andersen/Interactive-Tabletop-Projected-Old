var MAZE = MAZE || {};

MAZE.Intro = new Kiwi.State( "Intro" );

/**
* IntroState manages main-menu functionality for your game.
* Generally this State would switch to other sub 'states'
* which would handle the individual features.
*
* Right now we are just switching straight to the PlayState.
*/


MAZE.Intro.create = function () {

	Kiwi.State.prototype.create.call( this );

	game.states.switchState( "Play" );
};
