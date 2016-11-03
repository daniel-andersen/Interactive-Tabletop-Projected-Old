import cv2
from board import histogram_util


def compare_images(image1, image2, threshold=1.0):
    """
    Compares two images for significant differences.

    :param image1 First image
    :param image2 Second image
    :param threshold Maximum threshold delta
    :return: True, if there are significant differences, or else false
    """

    median_threshold_max = threshold

    return abs(image_comparison_score(image1) - image_comparison_score(image2)) > median_threshold_max


def image_comparison_score(image):
    """
    Calculates the image comparison score.

    :param image: Source image
    :return: The image comparison score
    """
    (height, width) = image.shape[:2]

    grayscaled_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized_image = histogram_util.equalize_image(grayscaled_image)

    histogram = histogram_util.histogram_from_image(equalized_image, 256)

    median = histogram_util.histogram_median(histogram, width * height)

    return median
