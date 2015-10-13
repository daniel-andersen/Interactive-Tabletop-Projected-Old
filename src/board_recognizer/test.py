import cv2
from board_recognizer import board_recognizer


def test():
    image = cv2.imread("board_recognizer/training/practice2b.png")
    image = cv2.resize(image, (500, 500))

    recognizer = board_recognizer.BoardRecognizer()
    descriptor = recognizer.find_board(image)

    if descriptor.is_recognized():
        cv2.imshow('frame', descriptor.board_image)
    else:
        cv2.imshow('frame', image)

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
