import cv2
import paper_recognizer

cap = cv2.VideoCapture(0)

recognizer = paper_recognizer.PaperRecognizer()

while True:
    # Capture frame-by-frame
    ret, image = cap.read()

    image = cv2.resize(image, (500, 500))

    corners = recognizer.recognize_paper(image)

    output_image = recognizer.get_output_image(0)
    if output_image is None:
        output_image = recognizer.get_output_image(0)

    output_image = image

    output_contour = recognizer.get_output_contour(0)
    if output_contour is None:
        output_contour = recognizer.get_output_contour(0)

    cv2.drawContours(output_image, output_contour, -1, (255, 0, 0), 3)

    if corners is not None:
        cv2.drawContours(output_image, [corners], 0, (0, 255, 0), 3)

    # Display the resulting frame
    cv2.imshow('frame', output_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

