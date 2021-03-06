import cv2
import numpy as np
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer
from board.tile_brick_detector import TileBrickDetector
from board.markers.shape_marker import ShapeMarker
from board.markers.triangle_marker import TriangleMarker
from board.markers.image_marker import ImageMarker
from board.board_areas.tiled_board_area import TiledBoardArea
from util import contour_util


def tiled_brick_detector_test():
    test_set = {
        "practice1": [
            ((0, 8), [(0, 8), (1, 8), (1, 7), (2, 8), (1, 9)]),
            ((2, 16), [(2, 16), (2, 15), (2, 14), (3, 16)]),
            ((6, 5), [(6, 5), (5, 5), (7, 5), (6, 6)]),
            ((10, 19), [(10, 19), (10, 18), (9, 18), (8, 18), (11, 18), (12, 18)]),
            ((14, 11), [(14, 11), (15, 11), (14, 10), (14, 9), (13, 9)]),
            ((17, 1), [(17, 1), (18, 1), (19, 1), (20, 1)]),
            ((17, 18), [(17, 18), (18, 18), (16, 18), (15, 18), (14, 18)]),
            ((22, 11), [(22, 11), (22, 10), (23, 10), (22, 12), (22, 13)]),
            ((28, 18), [(28, 18), (27, 18), (26, 18), (28, 17), (28, 16)]),
            ((29, 2), [(29, 2), (28, 2), (27, 2), (29, 3), (29, 4)]),
            ((31, 8), [(31, 8), (30, 8), (29, 8), (29, 7), (29, 9)]),
        ],
        "practice2": [
            ((2, 3), [(2, 3), (2, 4), (3, 3), (4, 3)]),
            ((2, 5), [(2, 5), (2, 4), (2, 6), (1, 6)]),
            ((2, 14), [(2, 14), (2, 13), (2, 12), (3, 13), (2, 15), (2, 16)]),
            ((6, 2), [(6, 2), (5, 2), (4, 2), (7, 2), (8, 2)]),
            ((6, 6), [(6, 6), (6, 5), (5, 5), (7, 5), (6, 7), (6, 8)]),
            ((7, 17), [(7, 17), (7, 16), (7, 15), (7, 18), (6, 18), (8, 18)]),
            ((11, 9), [(11, 9), (11, 8), (11, 7), (12, 9), (13, 9), (11, 10), (11, 11)]),
            #((13, 16), [(13, 16), (12, 16), (12, 15), (14, 16), (14, 15), (13, 17), (13, 18)]),
            ((16, 7), [(16, 7), (15, 7), (14, 7), (13, 7), (17, 7), (17, 6), (17, 8)]),
            ((16, 13), [(16, 13), (15, 13), (14, 13), (17, 13), (17, 12), (17, 14)]),
            ((20, 3), [(20, 3), (20, 2), (20, 1), (19, 3), (18, 3), (21, 3), (22, 3), (20, 4), (20, 5)]),
            ((21, 16), [(21, 16), (20, 16), (19, 16), (21, 15), (21, 14), (21, 17), (21, 18)]),
            ((24, 9), [(24, 9), (24, 8), (24, 7), (24, 10), (24, 11), (23, 10)]),
            ((26, 5), [(26, 5), (26, 4), (27, 4), (26, 6), (26, 7), (26, 8), (25, 6)]),
            ((27, 14), [(27, 14), (27, 13), (27, 12), (26, 14), (25, 14), (28, 14), (29, 14), (28, 15)]),
        ],
        "practice3": [
            ((1, 8), [(1, 8), (1, 7), (1, 6), (0, 8), (2, 8), (1, 9), (1, 10)]),
            ((3, 8), [(3, 8), (2, 8), (4, 8)]),
            ((9, 14), [(9, 14), (9, 13), (9, 15), (10, 15), (11, 15)]),
            ((13, 0), [(13, 0), (13, 1), (12, 1), (11, 1), (14, 1), (15, 1)]),
            ((17, 18), [(17, 18), (18, 18), (16, 18), (15, 18), (14, 18)]),
            ((20, 3), [(20, 3), (20, 2), (20, 1), (19, 3), (18, 3), (21, 3), (22, 3), (20, 4), (20, 5)]),
            ((22, 7), [(22, 7), (21, 7), (21, 6), (21, 5), (23, 7), (24, 7)]),
            ((26, 8), [(26, 8), (26, 7), (26, 6), (25, 7), (26, 9), (27, 9)]),
            ((27, 18), [(27, 18), (26, 18), (25, 18), (25, 17), (28, 18), (28, 17), (28, 16)]),
            ((29, 2), [(29, 2), (28, 2), (27, 2), (26, 2), (29, 3), (29, 4), (29, 5), (28, 4)]),
            ((29, 11), [(29, 11), (29, 10), (29, 9), (29, 8), (28, 9), (30, 11), (30, 12), (30, 13)]),
        ],
        "practice4": [
            ((3, 18), [(3, 18), (3, 17), (3, 16), (2, 16), (4, 16)]),
            ((4, 3), [(4, 3), (4, 2), (5, 2), (3, 3), (2, 3), (4, 4), (4, 5)]),
            ((5, 13), [(5, 13), (5, 12), (5, 11), (5, 10), (4, 13), (3, 13), (6, 13), (7, 13)]),
            ((10, 18), [(10, 18), (10, 19), (9, 18), (8, 18), (11, 18), (12, 18)]),
            ((17, 5), [(17, 5), (17, 4), (17, 3), (17, 6), (17, 7)]),
            ((17, 15), [(17, 15), (17, 14), (17, 13), (17, 12), (16, 13), (17, 16), (18, 16), (19, 16)]),
            ((18, 1), [(18, 1), (17, 1), (19, 1), (20, 1), (21, 1), (20, 2)]),
            ((21, 17), [(21, 17), (21, 16), (21, 15), (20, 16), (21, 18), (22, 18), (23, 18)]),
            ((27, 4), [(27, 4), (26, 4), (26, 5), (26, 6), (28, 4), (29, 4), (29, 3), (29, 5)]),
            ((28, 18), [(28, 18), (27, 18), (26, 18), (25, 18), (28, 17), (28, 16), (28, 15)]),
            ((31, 8), [(31, 8), (30, 8), (29, 8), (29, 7), (29, 9)]),
        ],
        "practice5": [
            ((31, 10), [(31, 10), (30, 10), (29, 10)]),
            ((0, 10), [(0, 10), (1, 10), (2, 10)]),
        ],
        "practice6": [
            (None, [(31, 10), (30, 10), (29, 10), (30, 11)]),
            (None, [(0, 10), (1, 10), (2, 10)]),
            (None, [(16, 0), (16, 1), (16, 2)]),
            (None, [(16, 19), (16, 18), (16, 17), (15, 18), (17, 18)]),
        ],
        "practice7": [
            (None, [(31, 10), (30, 10), (29, 10)]),
            (None, [(0, 10), (1, 10), (2, 10)]),
            (None, [(16, 0), (16, 1), (16, 2)]),
            (None, [(16, 19), (16, 18), (16, 17), (15, 18)]),
        ],
        "practice8": [
            (None, [(31, 10), (30, 10), (29, 10), (30, 9)]),
            (None, [(0, 10), (1, 10), (2, 10)]),
            (None, [(16, 0), (16, 1), (16, 2)]),
            (None, [(16, 19), (16, 18), (16, 17), (17, 18)]),
        ],
        "practice9": [
            (None, [(31, 10), (30, 10), (29, 10)]),
            (None, [(0, 10), (1, 10), (2, 10)]),
            (None, [(16, 19), (16, 18), (16, 17), (17, 18)]),
        ],
        "practice10": [
            (None, [(31, 10), (30, 10), (29, 10), (30, 9), (30, 11)]),
            (None, [(0, 10), (1, 10), (2, 10)]),
            (None, [(16, 19), (16, 18), (16, 17), (17, 18)]),
        ],
        "practice11": [
            (None, [(31, 10), (30, 10), (29, 10), (30, 11)]),
            (None, [(0, 10), (1, 10), (2, 10)]),
            (None, [(16, 19), (16, 18), (16, 17), (17, 18)]),
        ],
        "practice13": [
            (None, [[31,10],[30,10],[29,10],[30,9]]),
            (None, [[16,19],[16,18],[16,17]]),
            (None, [[0,10],[1,10],[2,10]]),
        ],
        "practice14": [
            (None, [[31, 10], [30, 10], [29, 10], [30, 11]]),
            (None, [[16, 19], [16, 18], [16, 17], [15, 18], [17, 18]]),
            (None, [[0, 10], [1, 10], [2, 10]]),
        ],
    }

    board_descriptor = BoardDescriptor()
    board_descriptor.corner_marker = TriangleMarker()
    board_descriptor.board_size = [1280, 800]
    board_descriptor.border_percentage_size = [0.0, 0.0]

    tiled_board_area = TiledBoardArea(tile_count=[32, 20], board_descriptor=board_descriptor)

    board_recognizer = BoardRecognizer()
    brick_detector = TileBrickDetector()

    failed = 0
    passed = 0

    for image_name in test_set.keys():
        for suffix in ["a", "b"]:
            image_filename = "board/training/" + image_name + suffix + ".png"

            tests = test_set[image_name]

            image = cv2.imread(image_filename)
            if image is None:
                continue

            board_descriptor.snapshot = board_recognizer.find_board(image, board_descriptor)

            if not board_descriptor.is_recognized():
                print("Board not recognized for filename %s" % image_filename)
                failed += 1
                break

            for brick_position, tile_array in tests:
                valid_position = brick_position if suffix == "b" else None
                tile = brick_detector.find_brick_among_tiles(tiled_board_area, tile_array)[0]
                if tile != valid_position:
                    print("Test failed. Brick supposed to be at: %s but was at: %s. Image: %s" % (valid_position, tile, image_filename))
                    failed += 1
                    continue
                passed += 1

    print("%i tests passed, %i failed" % (passed, failed))


def shape_marker_test():
    test_set = {
        "triangle": {
            "marker": ShapeMarker(np.int32([[0, 0], [100, 0], [0, 100]]).reshape(-1, 1, 2), max_area=0.5),
            "detect": [1, 2]
        },
        "square": {
            "marker": ShapeMarker(np.int32([[0, 0], [100, 0], [100, 100], [0, 100]]).reshape(-1, 1, 2)),
            "detect": [6]
        },
        "castle": {
            "marker": ShapeMarker(np.int32([[0, 0], [10, 0], [10, 20], [20, 20], [20, 10], [30, 10], [30, 20], [40, 20], [40, 0], [50, 0], [50, 50], [30, 50], [30, 40], [20, 40], [20, 50], [0, 50]]).reshape(-1, 1, 2), distance_tolerance=0.2, angle_tolerance=0.65),
            "detect": [3, 5, 7]
        },
        "star": {
            "marker": ShapeMarker(marker_image=cv2.imread("board/training/marker_star.png"), distance_tolerance=0.50, angle_tolerance=0.35),
            "detect": [11, 12]
        },
        "dog": {
            "marker": ImageMarker(marker_image=cv2.imread("board/training/marker_dog.png")),
            "detect": [13]
        }
    }

    failed = 0
    passed = 0

    marker_test_images_count = 13

    for marker_name in test_set.keys():
        marker = test_set[marker_name]["marker"]

        for i in range(1, marker_test_images_count + 1):
            #if marker_name != "square" or i != 13:
            #    continue

            image_filename = "board/training/marker_test_{0}.png".format(i)
            image = cv2.imread(image_filename)
            if image is None:
                continue

            marker_result = marker.find_marker_in_image(image)

            #if contour is not None:
            #    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #    contour_util.draw_contour(image, contour=contour, scale=1)
            #    cv2.waitKey(0)

            expected_found = i in test_set[marker_name]["detect"]
            found = marker_result is not None

            if found != expected_found:
                print("Test failed: %s marker, image %i. Marker found: %s but was expected: %s." % (marker_name, i, "YES" if found else "NO", "YES" if expected_found else "NO"))
                failed += 1
                continue
            passed += 1

    print("%i tests passed, %i failed" % (passed, failed))

def shape_marker_camera_test():
    marker_image = cv2.imread("board/training/marker_star.png")
    marker = ShapeMarker(marker_image=marker_image, distance_tolerance=0.50, angle_tolerance=0.35)

    #image = cv2.imread("board/training/marker_star.png")
    #print(marker.find_marker_in_image(image))
    #return

    cap = cv2.VideoCapture(0)
    while True:
        res, image = cap.read()
        image = cv2.resize(image, (640, 480))

        marker_result = marker.find_marker_in_image(image)
        if marker_result is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            contour_util.draw_contour(image=image, contour=marker_result["contour"], scale=1, name="Marker")
        else:
            cv2.imshow("Marker", image)

        cv2.waitKey(10)


def board_detector_test():
    test_set = {
        "board1": True,
        "board2": True,
        "board3": True,
        "board4": True,
        "board5": True,
        "board6": True,
        "board7": True,
        "board8": True,
        "board9": True,
        "board10": True,
        "board11": True,
        "board12": True,
        "board13": True,
        "board14": True,
        "board15": True,
        "board16": True,
    }

    board_descriptor = BoardDescriptor()
    board_descriptor.board_size = [1280, 800]
    board_descriptor.border_percentage_size = [0.0, 0.0]

    board_recognizer = BoardRecognizer()

    failed = 0
    passed = 0

    for image_name in test_set.keys():
        image_filename = "board/training/" + image_name + ".png"

        image = cv2.imread(image_filename)
        if image is None:
            continue

        board_descriptor.snapshot = board_recognizer.find_board(image, board_descriptor)
        is_recognized = board_descriptor.is_recognized()

        if is_recognized != test_set[image_name]:
            print("Board not recognized for filename %s" % image_filename)
            failed += 1
        else:
            passed += 1

    print("%i tests passed, %i failed" % (passed, failed))


def custom_test():
    board_descriptor = BoardDescriptor()
    board_descriptor.board_size = [1280, 800]
    board_descriptor.border_percentage_size = [0.0, 0.0]
    board_descriptor.tile_count = [32, 20]

    tiled_board_area = TiledBoardArea(tile_count=[32, 20], board_descriptor=board_descriptor)

    board_recognizer = BoardRecognizer()

    brick_detector = TileBrickDetector()

    #cap = cv2.VideoCapture(0)

    while True:
        image = cv2.imread("board/training/board1.png")
        #_, image = cap.read()

        board_descriptor.snapshot = board_recognizer.find_board(image, board_descriptor)

        if board_descriptor.is_recognized():
            contour = np.int32(board_descriptor.snapshot.board_corners).reshape(-1, 1, 2)
            cv2.drawContours(image, [contour], -1, (255,0,255), 2)

            tiles = [[31, 10], [30, 10], [29, 10], [30, 11]]
            tile = brick_detector.find_brick_among_tiles(tiled_board_area, tiles)[0]
            print(tile)
            #cv2.imshow('Snapshot', descriptor.snapshot.board_image)
            #cv2.imshow('Board Canvas', descriptor.board_canvas())
            #cv2.imshow('Board Tile', descriptor.tile(9, 0))
            cv2.imshow('Board Tiles', board_descriptor.tile_strip(tiles))

            image2 = cv2.cvtColor(board_descriptor.tile_strip(tiles).copy(), cv2.COLOR_BGR2GRAY)
            _, image2 = cv2.threshold(image2, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            cv2.imshow('OTSU Board Tiles', image2)

        else:
            print("Board not found!")

        cv2.imshow('Board Image', image)
        cv2.waitKey(0)

    cv2.destroyAllWindows()
