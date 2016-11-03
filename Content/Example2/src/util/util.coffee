class Util
    @randomInRange: (min, max) -> Math.floor(Math.random() * (max - min) + min)
    @currentTimeSeconds: -> new Date().getTime() / 1000.0

    @fadeInElement: (element, duration, kiwiState, delay = 0, onCompleteCallback = undefined ) ->
        element.alpha = 0.0
        element.visible = true

        tween = kiwiState.game.tweens.create(element)
        tween.delay(delay)
        if onCompleteCallback?
            tween.onComplete((a, b) => onCompleteCallback())
        tween.to({ alpha: 1.0 }, duration, Kiwi.Animations.Tweens.Easing.Linear.In, true)

    @fadeOutElement: (element, duration, kiwiState, onCompleteCallback = undefined ) ->
        tween = kiwiState.game.tweens.create(element)
        tween.onComplete((a, b) =>
            element.visible = false
            if onCompleteCallback? then onCompleteCallback()
        )
        tween.to({ alpha: 0.0 }, duration, Kiwi.Animations.Tweens.Easing.Linear.In, true)

    @centerElement: (element, kiwiState) ->
        element.x = (kiwiState.game.stage.width - element.width) / 2.0
        element.y = (kiwiState.game.stage.height - element.height) / 2.0

    @positionElement: (element, x, y, kiwiState) ->
        element.x = (kiwiState.game.stage.width * x) - (element.width / 2.0)
        element.y = (kiwiState.game.stage.height * y) - (element.height / 2.0)

class Position
    constructor: (@x = 0, @y = 0) ->

    equals: (position) -> @x == position.x and @y == position.y
