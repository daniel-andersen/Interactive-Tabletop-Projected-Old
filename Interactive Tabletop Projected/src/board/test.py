import cv2
import numpy as np
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer
from board.tile_brick_detector import TileBrickDetector


def run_tests():
    descriptor = BoardDescriptor()
    descriptor.border_percentage_size = (0.0, 0.0)
    descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
    descriptor.tile_count = [32, 20]

    board_recognizer = BoardRecognizer()
    brick_detector = TileBrickDetector()

    test_set = {
        "board/training/practice1b.png": [
            ((3, 2), [(3, 4), (3, 3), (3, 2), (3, 1), (4, 1)]),
            ((5, 11), [(4, 10), (5, 10), (5, 11), (5, 12), (5, 13), (6, 12)]),
            ((10, 3), [(10, 1), (10, 2), (10, 3), (11, 3), (12, 3), (10, 4), (10, 5)]),
            ((14, 16), [(14, 14), (14, 15), (12, 16), (13, 16), (14, 16), (15, 16), (16, 16)]),
        ]
    }

    failed = 0
    passed = 0

    for image_filename in test_set.keys():
        tests = test_set[image_filename]

        image = cv2.imread(image_filename)

        descriptor.snapshot = board_recognizer.find_board(image, descriptor.corner_marker)

        if not descriptor.is_recognized():
            print("Board not recognized for filename %s" % image_filename)
            failed += 1
            break

        for brick_position, tile_array in tests:
            tile = brick_detector.find_brick_among_tiles(descriptor, tile_array)
            if tile != brick_position:
                print("Test failed. Brick supposed to be at: %s but was at: %s" % (brick_position, tile))
                failed += 1
                continue
            passed += 1

    print("%i tests passed, %i failed" % (passed, failed))


def test():
    descriptor = BoardDescriptor()
    descriptor.border_percentage_size = (0.0, 0.0)
    descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
    descriptor.tile_count = [32, 20]

    board_recognizer = BoardRecognizer()
    brick_detector = TileBrickDetector()

    cap = cv2.VideoCapture(0)

    while True:
        image = cv2.imread("board/training/practice1b.png")
        #_, image = cap.read()

        descriptor.snapshot = board_recognizer.find_board(image, descriptor.corner_marker)

        if descriptor.is_recognized():
            contour = np.int32(descriptor.snapshot.board_corners).reshape(-1, 1, 2)
            cv2.drawContours(image, [contour], -1, (255,0,255), 2)

            tiles = [(10, 1), (10, 2), (10, 3), (11, 3), (12, 3), (10, 4), (10, 5)]
            tile = brick_detector.find_brick_among_tiles(descriptor, tiles)
            print(tile)
            #cv2.imshow('Snapshot', descriptor.snapshot.board_image)
            #cv2.imshow('Board Canvas', descriptor.board_canvas())
            #cv2.imshow('Board Tile', descriptor.tile(9, 0))
            cv2.imshow('Board Tiles', descriptor.tile_strip(tiles))
        else:
            print("Not found!")
        cv2.imshow('Board Image', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
