import cv2
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer
from board.tile_brick_detector import TileBrickDetector


def test():
    descriptor = BoardDescriptor()
    descriptor.border_percentage_size = (0.0, 0.0)
    descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
    descriptor.tile_count = [30, 20]

    recognizer = BoardRecognizer()

    cap = cv2.VideoCapture(0)

    while True:
        image = cv2.imread("board/training/practice16.png")
        #_, image = cap.read()

        descriptor.snapshot = recognizer.find_board(image, descriptor.corner_marker)

        if descriptor.is_recognized():
            #p = TileBrickDetector().find_brick_among_tiles(descriptor, [(9, 0), (9, 1), (9, 2)])
            #print(p)
            cv2.imshow('Board Image', descriptor.snapshot.board_image)
            #cv2.imshow('Board Canvas', descriptor.board_canvas())
            #cv2.imshow('Board Tile', descriptor.tile(9, 0))
            #cv2.imshow('Board Tiles', descriptor.tile_strip([(9, 0), (9, 1), (9, 2)]))
        else:
            cv2.imshow('Board Image', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
