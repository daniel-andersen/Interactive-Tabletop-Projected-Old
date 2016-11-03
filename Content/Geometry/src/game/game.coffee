GEOMETRY = GEOMETRY or {}
GEOMETRY.Game = new Kiwi.State("Game")

geometryGame = null

GEOMETRY.Game.preload = ->
    @addImage("corners", "assets/img/game/corners.png")

GEOMETRY.Game.create = ->
    Kiwi.State::create.call(this)

    geometryGame = new GeometryGame(this)
    geometryGame.start()

GEOMETRY.Game.shutDown = ->
    Kiwi.State::shutDown.call(this)
    geometryGame.stop()

GEOMETRY.Game.update = ->
    Kiwi.State::update.call(this)
    geometryGame.update()



GeometryType =
    TRIANGLE: 0
    SQUARE: 1
    CIRCLE: 2
    OTHER: 3


class GeometryGame

    constructor: (@kiwiState) ->
        @client = new Client()

    start: ->
        @setup()
        @setupUi()

        @client.connect(
          (() => @reset()),
          ((json) => @onMessage(json))
        )

    stop: ->
        @client.disconnect()

    reset: ->
        @client.reset([1600, 1200], (action, payload) =>
            @client.enableDebug()
            @initializeBoard()
        )

    onMessage: (json) ->

    update: ->

    setup: ->

        # The scale of the physical board in centimeters
        @boardCentimeterScale = 85.0
        @verticalAspectScale = @kiwiState.game.stage.height / @kiwiState.game.stage.width

        # An array of recognized geometry figures
        @geometry = []

        # Shape history count
        @geometryRelaxationTime = 1.0

        # Minimum move distance before UI is updated
        @geometryUpdateMinMoveDistance = 0.01

    setupUi: ->

        # Show canvas
        content = document.getElementById("content")
        content.style.visibility = "visible"

        # Corners (for tracking board)
        @corners = new Kiwi.GameObjects.StaticImage(@kiwiState, @kiwiState.textures.corners, 0, 0)
        @kiwiState.addChild(@corners)

    initializeBoard: ->
        @client.initializeBoard(undefined, undefined, (action, payload) =>
            @initializeBoardAreas()
        )

    initializeBoardAreas: ->

        # Whole board area
        @wholeBoardAreaId = 0
        @client.initializeBoardArea(0.0, 0.0, 1.0, 1.0, @wholeBoardAreaId, (action, payload) =>
            @startNewGame()
        )

    startNewGame: ->
        setTimeout(() =>
            @findContours()
        , 2000)



    # MARKER HANDLING

    findContours: ->
        @client.requestContours(@wholeBoardAreaId, 0.04, undefined, (action, payload) =>
            @foundContours(payload)
            @findContours()
        )

    foundContours: (payload) ->

        # Update history
        for geometryInfo in @geometry.slice()

            # Update history
            while geometryInfo["history"].length > 0 and geometryInfo["history"][0] < Util.currentTimeSeconds() - @geometryRelaxationTime
                geometryInfo["history"].shift()

            # Remove geometry if no longer visible
            if geometryInfo["history"].length == 0
                @removeGeometryUi(geometryInfo)
                @geometry.splice(@geometry.indexOf(geometryInfo), 1)

        # Update geometry with found contours
        @updateGeometry(payload["contours"], payload["hierarchy"])

    updateGeometryUi: (geometryInfo) ->
        console.log("Updating UI for geometry of type " + @contourType(geometryInfo["contourDict"]))

        # Remove current UI elements
        @removeGeometryUi(geometryInfo)

        # Add UI elements
        switch geometryInfo["type"]
            when GeometryType.TRIANGLE then @updateTriangleShapeUi(geometryInfo)
            when GeometryType.SQUARE then @updateSquareShapeUi(geometryInfo)

    updateTriangleShapeUi: (geometryInfo) ->
        @updateSideLengthsUi(geometryInfo)
        @updateAreaUi(geometryInfo)

    updateSquareShapeUi: (geometryInfo) ->
        @updateSideLengthsUi(geometryInfo)
        @updateAreaUi(geometryInfo)

    updateSideLengthsUi: (geometryInfo) ->

        contourDict = geometryInfo["contourDict"]
        contour = contourDict["contour"]
        scaledContour = @aspectScaledContour(contour)

        # Annotate lines
        for index in [0..contour.length - 1]
            index1 = index
            index2 = (index + 1) % contour.length

            center = @contourCenter(contourDict)
            center = [center[0] * @kiwiState.game.stage.width, center[1] * @kiwiState.game.stage.height]

            p1 = contour[index]
            p2 = contour[(index + 1) % contour.length]

            p = [((p1[0] + p2[0]) / 2.0) * @kiwiState.game.stage.width, ((p1[1] + p2[1]) / 2.0) * @kiwiState.game.stage.height]
            p = @translateAwayFromCenter(p, center)

            length = @pointsDistance(scaledContour[index1], scaledContour[index2]) * @boardCentimeterScale

            text = new Kiwi.GameObjects.Textfield(@kiwiState, length.toFixed(0), p[0], p[1], "#FF0000", 12)
            text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER
            element = @kiwiState.addChild(text)
            geometryInfo["uiElements"]["line" + index] = element

            text = new Kiwi.GameObjects.Textfield(@kiwiState, "cm", p[0], p[1] + 12, "#FF0000", 12)
            text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER
            element = @kiwiState.addChild(text)
            geometryInfo["uiElements"]["line" + index + "_cm"] = element

    updateAreaUi: (geometryInfo) ->

        contourDict = geometryInfo["contourDict"]

        # Annotate area
        center = @contourCenter(contourDict)
        center = [center[0] * @kiwiState.game.stage.width, center[1] * @kiwiState.game.stage.height]

        area = contourDict["area"] * (@boardCentimeterScale * @verticalAspectScale) * @boardCentimeterScale

        text = new Kiwi.GameObjects.Textfield(@kiwiState, area.toFixed(0), center[0], center[1], "#00FF00", 12)
        text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER
        element = @kiwiState.addChild(text)
        geometryInfo["uiElements"]["area"] = element

        text = new Kiwi.GameObjects.Textfield(@kiwiState, "cm2", center[0], center[1] + 12, "#00FF00", 12)
        text.textAlign = Kiwi.GameObjects.Textfield.TEXT_ALIGN_CENTER
        element = @kiwiState.addChild(text)
        geometryInfo["uiElements"]["area_cm2"] = element

    removeGeometryUi: (geometryInfo) ->
        for name, element of geometryInfo["uiElements"]
            element.destroy()
            console.log("Removing element: " + element)
        geometryInfo["uiElements"] = {}

    aspectScaledContour: (contour) ->
        return ([p[0], p[1] * @verticalAspectScale] for p in contour)

    updateGeometry: (contours, hierarchy) ->

        # Mark all geometry as not matched
        for geometryInfo in @geometry
            geometryInfo["matchedContourIndex"] = -1

        # Mark all contours as not matched
        matchedContourIndices = (-1 for i in [0..contours.length-1])

        # Match shape and position for all contours
        for index in [0..contours.length-1]
            if not @isValidContour(contours, hierarchy, index) then continue
            contourDict = contours[index]
            for geometryInfo in @geometry
                if geometryInfo["matchedContourIndex"] == -1 and @isSameShape(contourDict, geometryInfo["contourDict"]) and @isSamePosition(contourDict, geometryInfo["contourDict"])
                    geometryInfo["matchedContourIndex"] = index
                    matchedContourIndices[index] = geometryInfo["id"]
                    break

        # Match only shape for all remaining contours
        for index in [0..contours.length-1]
            if not @isValidContour(contours, hierarchy, index) then continue
            contourDict = contours[index]
            for geometryInfo in @geometry
                if geometryInfo["matchedContourIndex"] == -1 and @isSameShape(contourDict, geometryInfo["contourDict"])
                    geometryInfo["matchedContourIndex"] = index
                    matchedContourIndices[index] = geometryInfo["id"]
                    break

        # Create new geometry for all unmatched contours
        for index in [0..contours.length-1]
            if matchedContourIndices[index] == -1
                contourDict = contours[index]
                if @isValidContour(contours, hierarchy, index)
                    geometryInfo = @newGeometry(contourDict, hierarchy)
                    geometryInfo["matchedContourIndex"] = index
                    matchedContourIndices[index] = geometryInfo["id"]
                    console.log("Added new geometry of type: " + @contourType(contourDict))

        # Update all geometry
        for geometryInfo in @geometry
            if geometryInfo["matchedContourIndex"] == -1 then continue

            matchedContourDict = contours[geometryInfo["matchedContourIndex"]]
            currentContourDict = geometryInfo["contourDict"]

            # Add timestamp to history
            geometryInfo["history"].push(Util.currentTimeSeconds())

            # Update model
            @updateGeometryInfo(geometryInfo, matchedContourDict)

            # Update UI
            if @shouldUpdateGeometryUi(geometryInfo, currentContourDict, matchedContourDict)
                @updateGeometryUi(geometryInfo)

    updateGeometryInfo: (geometryInfo, contourDict) ->
        geometryInfo["contourDict"] = contourDict

    newGeometry: (contourDict, hierarchy) ->
        geometryInfo = {
            "id": Util.randomInRange(0, 100000)
            "contourDict": contourDict
            "hierarchy": hierarchy
            "type": @contourType(contourDict)
            "history": []
            "uiElements": {}
        }
        @geometry.push(geometryInfo)
        return geometryInfo

    isSameShape: (contourDict1, contourDict2) ->

        contour1 = contourDict1["contour"]
        contour2 = contourDict2["contour"]

        # Check type
        if @contourType(contourDict1) != @contourType(contourDict2)
            return false

        # Check arc length
        arcLengthRatio = Math.max(contour1["arclength"], contour2["arclength"]) / Math.min(contour1["arclength"], contour2["arclength"])

        if arcLengthRatio > 1.1
            return false

        # Check area
        areaRatio = Math.max(contour1["area"], contour2["area"]) / Math.min(contour1["area"], contour2["area"])

        if areaRatio > 1.1
            return false

        # Same same
        return true

    isSamePosition: (contourDict1, contourDict2) ->
        return @contourDistance(contourDict1, contourDict2) < 0.05

    shouldUpdateGeometryUi: (geometryInfo, currentContourDict, newContourDict) ->
        newContour = newContourDict["contour"]
        currentContour = currentContourDict["contour"]

        # Check any UI currently
        if Object.keys(geometryInfo["uiElements"]).length == 0
            return true

        # Match first point
        matchIndex = undefined

        p1 = currentContour[0]
        for index in [0..newContour.length - 1]
            p2 = newContour[index]
            if @pointsDistance(p1, p2) < @geometryUpdateMinMoveDistance
                matchIndex = index

        # First point not matched
        if not matchIndex? then return true

        # Match remaining points in both directions
        matchLeft = true
        matchRight = true

        for index in [0..currentContour.length - 1]
            p1 = currentContour[index]
            p2 = newContour[(matchIndex + index) % newContour.length]
            if @pointsDistance(p1, p2) >= @geometryUpdateMinMoveDistance
                matchRight = false

            p2 = newContour[(matchIndex - index + newContour.length) % newContour.length]
            if @pointsDistance(p1, p2) >= @geometryUpdateMinMoveDistance
                matchLeft = false

        return not matchLeft and not matchRight

    contourDistance: (contourDict1, contourDict2) ->
        center1 = @contourCenter(contourDict1)
        center2 = @contourCenter(contourDict2)

        return @pointsDistance(center1, center2)

    pointsDistance: (p1, p2) ->
        deltaX = p1[0] - p2[0]
        deltaY = p1[1] - p2[1]
        return Math.sqrt(deltaX*deltaX + deltaY*deltaY)

    isValidContour: (contours, hierarchy, index) ->

        contourDict = contours[index]

        # Unknown contour type
        if @contourType(contourDict) == GeometryType.OTHER then return false

        # Area too small. Just noise.
        if contourDict["area"] < 0.001 then return false

        # Area too large. Might be border.
        if contourDict["area"] > 0.9 then return false

        # Must have no valid children
        childIndex = hierarchy[index][2]
        if childIndex != -1 #and @isValidContour(contours, hierarchy, childIndex)
            return false

        return true

    contourType: (contourDict) ->

        # Triangle
        if contourDict["contour"].length == 3 then return GeometryType.TRIANGLE

        # Square
        if contourDict["contour"].length == 4 then return GeometryType.SQUARE

        return GeometryType.OTHER

    contourCenter: (contourDict) ->
        contour = contourDict["contour"]

        center = [0.0, 0.0]

        for p in contour
            center[0] += p[0]
            center[1] += p[1]

        center[0] /= contour.length
        center[1] /= contour.length

        return center

    translateAwayFromCenter: (p, center) ->
        distance = @pointsDistance(p, center)
        if distance == 0
            return p

        delta = [p[0] - center[0], p[1] - center[1]]
        unit = [delta[0] / distance, delta[1] / distance]

        return [center[0] + (unit[0] * (distance + 50)), center[1] + (unit[1] * (distance + 50))]
