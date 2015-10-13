import cv2
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer


def test():
    image = cv2.imread("board/training/practice2b.png")
    image = cv2.resize(image, (500, 500))

    descriptor = BoardDescriptor()
    descriptor.border_percentage_size = (0.0184, 0.0336)
    descriptor.tile_count = [18, 15]

    recognizer = BoardRecognizer()
    recognizer.find_board(image, descriptor)

    if descriptor.is_recognized():
        cv2.imshow('Board Image', descriptor.snapshot.board_image)
        cv2.imshow('Board Canvas', descriptor.board_canvas())
        cv2.imshow('Board Tile', descriptor.tile(9, 0))
        cv2.imshow('Board Tiles', descriptor.tiles([(9, 0), (9, 1), (1, 6)]))

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
