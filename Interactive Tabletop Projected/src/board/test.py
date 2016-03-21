import cv2
import numpy as np
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer
from board.tile_brick_detector import TileBrickDetector


def run_tests():
    board_descriptor = BoardDescriptor()
    board_descriptor.board_size = [1280, 800]
    board_descriptor.border_percentage_size = [0.0, 0.0]
    board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
    board_descriptor.tile_count = [32, 20]

    board_recognizer = BoardRecognizer()
    brick_detector = TileBrickDetector()

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
    }

    failed = 0
    passed = 0

    for image_name in test_set.keys():
        for suffix in ["a", "b"]:
            image_filename = "board/training/" + image_name + suffix + ".png"

            tests = test_set[image_name]

            image = cv2.imread(image_filename)

            board_descriptor.snapshot = board_recognizer.find_board(image, board_descriptor)

            if not board_descriptor.is_recognized():
                print("Board not recognized for filename %s" % image_filename)
                failed += 1
                break

            for brick_position, tile_array in tests:
                valid_position = brick_position if suffix == "b" else None
                tile = brick_detector.find_brick_among_tiles(board_descriptor, tile_array)
                if tile != valid_position:
                    print("Test failed. Brick supposed to be at: %s but was at: %s. Image: %s" % (valid_position, tile, image_filename))
                    failed += 1
                    continue
                passed += 1

    print("%i tests passed, %i failed" % (passed, failed))


def test():
    board_descriptor = BoardDescriptor()
    board_descriptor.board_size = [1280, 800]
    board_descriptor.border_percentage_size = [0.0, 0.0]
    board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
    board_descriptor.tile_count = [32, 20]

    board_recognizer = BoardRecognizer()

    brick_detector = TileBrickDetector()

    #cap = cv2.VideoCapture(0)

    while True:
        image = cv2.imread("board/training/practice1b.png")
        #_, image = cap.read()

        board_descriptor.snapshot = board_recognizer.find_board(image, board_descriptor)

        if board_descriptor.is_recognized():
            contour = np.int32(board_descriptor.snapshot.board_corners).reshape(-1, 1, 2)
            cv2.drawContours(image, [contour], -1, (255,0,255), 2)

            tiles = [(6, 5), (5, 5), (7, 5), (6, 6)]
            tile = brick_detector.find_brick_among_tiles(board_descriptor, tiles)
            print(tile)
            #cv2.imshow('Snapshot', descriptor.snapshot.board_image)
            #cv2.imshow('Board Canvas', descriptor.board_canvas())
            #cv2.imshow('Board Tile', descriptor.tile(9, 0))
            cv2.imshow('Board Tiles', board_descriptor.tile_strip(tiles))

            image2 = cv2.cvtColor(board_descriptor.tile_strip(tiles).copy(), cv2.COLOR_BGR2GRAY)
            _, image2 = cv2.threshold(image2, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            cv2.imshow('OTSU Board Tiles', image2)

        else:
            print("Not found!")

        cv2.imshow('Board Image', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
