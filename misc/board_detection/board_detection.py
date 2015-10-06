import cv2
import board_recognizer
import brick_recognizer

cap = cv2.VideoCapture(0)

boardRecogizer = board_recognizer.BoardRecognizer()
brickRecognizer = brick_recognizer.BrickRecognizer()

while True:
    # Capture frame-by-frame
    #ret, image = cap.read()
    image = cv2.imread("training/practice2b.png")

    image = cv2.resize(image, (500, 500))



    # Recognizer board
    corners = boardRecogizer.recognize_paper(image)

    output_image = boardRecogizer.get_output_image(0)
    if output_image is None:
        output_image = boardRecogizer.get_output_image(0)

    if corners is not None:
        cv2.drawContours(output_image, [corners], 0, (0, 255, 0), 3)



    # Recognizer bricks
    keypoints = brickRecognizer.recognize_bricks(image)
    output_image = brickRecognizer.draw_bricks_on_image(output_image, keypoints)



    # Display the resulting frame
    cv2.imshow('frame', output_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

