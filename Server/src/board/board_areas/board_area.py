import cv2
from random import randint
from threading import RLock
from server import globals
from board import histogram_util
from board.board_descriptor import BoardDescriptor


class BoardArea(object):
    """
    Represents a description of a board area.

    Field variables:
    board_area_pct -- [x1, y1, x2, y2] in percentage [0..1]
    board_descriptor -- Board descriptor
    area_image -- Extracted area image
    """
    lock = RLock()
    extracted_area_images = {}
    extracted_grayscaled_area_images = {}
    foreground_mask = None

    def __init__(self, area_id=None, board_area_pct=[0.0, 0.0, 1.0, 1.0], board_descriptor=None):
        """
        Initializes a tiled board area.

        :param area_id: Area id. Autogenerated if None.
        :param board_area_pct: Board area in percentage of board [x1, y1, x2, y2]
        :param board_descriptor: Board descriptor. If None, global board descriptor is used.
        """
        self.area_id = area_id if area_id is not None else randint(0, 100000)
        self.board_area_pct = board_area_pct
        self.board_descriptor = board_descriptor if board_descriptor is not None else globals.board_descriptor
        self.background_subtractor = cv2.BackgroundSubtractorMOG2(history=5, varThreshold=16)
        self.current_stability_score = 1.0
        self.current_board_snapshot_id = None

    def area_image(self, snapshot_size=BoardDescriptor.SnapshotSize.SMALL):
        """
        Extracts area image from board snapshot.

        :param snapshot_size: Snapshot size to use
        :return Extracted area image
        """

        with self.lock:

            # Check if board is recognized
            if not self.board_descriptor.is_recognized():
                return None

            # Check if snapshot has changed
            if self.current_board_snapshot_id is not self.board_descriptor.snapshot.id:
                self.extracted_area_images = {}
                self.extracted_grayscaled_area_images = {}

            # Return pre-processed area image
            if snapshot_size in self.extracted_area_images:
                return self.extracted_area_images[snapshot_size]

            # Save snapshot ID
            self.current_board_snapshot_id = self.board_descriptor.snapshot.id

            # Get board canvas image
            board_image = self.board_descriptor.board_canvas(snapshot_size)
            image_height, image_width = board_image.shape[:2]

            # Extract area image
            x1 = int(float(image_width) * self.board_area_pct[0])
            y1 = int(float(image_height) * self.board_area_pct[1])
            x2 = int(float(image_width) * self.board_area_pct[2])
            y2 = int(float(image_height) * self.board_area_pct[3])

            self.extracted_area_images[snapshot_size] = board_image[y1:y2, x1:x2]

            return self.extracted_area_images[snapshot_size]

    def grayscaled_area_image(self, snapshot_size=BoardDescriptor.SnapshotSize.SMALL):
        """
        Extracts grayscaled area image from board snapshot.

        :param snapshot_size: Snapshot size to use
        :return Extracted area image
        """

        with self.lock:

            # Check if board is recognized
            if not self.board_descriptor.is_recognized():
                return None

            # Already extracted image
            if self.current_board_snapshot_id is self.board_descriptor.snapshot.id:
                if snapshot_size in self.extracted_grayscaled_area_images:
                    return self.extracted_grayscaled_area_images[snapshot_size]

            # Extract image
            image = self.area_image(snapshot_size)

            # Grayscale image
            self.extracted_grayscaled_area_images[snapshot_size] = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            return self.extracted_grayscaled_area_images[snapshot_size]

    def update_stability_score(self):

        with self.lock:

            # Get area image
            image = self.grayscaled_area_image(BoardDescriptor.SnapshotSize.SMALL)
            if self.foreground_mask is not None:
                mask_height, mask_width = self.foreground_mask.shape[:2]
                image = cv2.resize(image, (mask_width, mask_height))

            # Update foreground mask with area image
            self.foreground_mask = self.background_subtractor.apply(image, learningRate=0.5)

            mask_height, mask_width = self.foreground_mask.shape[:2]

            # Calculate stability score
            histogram = histogram_util.histogram_from_bw_image(self.foreground_mask)
            histogram_median = histogram_util.histogram_median(histogram, mask_width * mask_height)
            self.current_stability_score = 1.0 - (histogram_median / 255.0)

            #image_height, image_width = image.shape[:2]
            #print("Score %i: %f --- %i, %i" % (self.area_id, self.current_stability_score, image_width, image_height))
            #cv2.imwrite("image_%i.png" % self.area_id, image)
            #cv2.imwrite("mask_%i.png" % self.area_id, self.foreground_mask)

    def stability_score(self):
        with self.lock:
            return self.current_stability_score
