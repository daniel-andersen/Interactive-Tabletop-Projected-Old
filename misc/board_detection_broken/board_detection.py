import cv2

while True:
    image = cv2.imread("training/practice2b.png")

    image = cv2.resize(image, (500, 500))

    lineDetector = cv2.createLineSegmentDetector()

    lines = lineDetector.detect(image)

    lineDetector.drawSegments(image, lines)

    # Display the resulting frame
    cv2.imshow('frame', output_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

