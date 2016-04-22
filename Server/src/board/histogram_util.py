import cv2


def equalize_image(image):
    """
    Equalizes the given image.

    :param image: Source image
    :return: Equalized image
    """
    return cv2.equalizeHist(image)


def histogram_median(histogram, image_size):
    """
    Calculates the histogram median.

    :param histogram: Histogram
    :param image_size: Image size
    :return: Histogram median
    """
    median = 0
    for i in range(0, len(histogram)):
        median += float(histogram[i]) * float(i) / float(image_size)
    return median


def histogram_from_image(image, bin_count=256):
    """
    Calculates the histogram for the image.

    :param image: Source image
    :param bin_count: Bin count
    :return: Histogram for image
    """
    return cv2.calcHist([image], [0], None, [bin_count], [0, 256])


def histogram_from_bw_image(image, bin_count=256):
    """
    Calculates the histogram for a black/white image.

    :param image: Source image
    :param bin_count: Bin count
    :return: Histogram for image
    """
    return histogram_from_image(image, bin_count)
