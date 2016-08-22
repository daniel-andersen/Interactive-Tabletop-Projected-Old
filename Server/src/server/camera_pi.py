import cv2
import time
from threading import Thread
from threading import Lock
from picamera.array import PiRGBArray
from picamera import PiCamera


class Camera(object):
    stopped = False
    image = None
    camera = None
    raw_capture = None
    stream = None
    lock = Lock()

    def start(self, resolution=(640, 480), framerate=16):
        """
        Starts camera input in a new thread.

        :param resolution Resolution
        :param framerate Framerate
        """
        self.stopped = False

        # Initialize camera
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate

        self.raw_capture = PiRGBArray(self.camera, size=resolution)
        self.raw_capture.truncate(0)

        self.stream = self.camera.capture_continuous(self.raw_capture, format="bgr", use_video_port=True)

        # Start thread
        thread = Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()

    def stop(self):
        """
        Stops camera input.
        """
        self.stopped = True

    def read(self):
        """
        Returns the most recent image read from the camera input.
        """
        with self.lock:
            return self.image

    def update(self):
        """
        Grabs next image from camera.
        """
        for f in self.stream:

            # Sleep a while
            time.sleep(0.01)

            # Grab image
            rotated_image = f.array
            self.raw_capture.truncate(0)

            # Rotate image 180 degrees
            (height, width) = rotated_image.shape[:2]
            center = (width / 2, height / 2)
            matrix = cv2.getRotationMatrix2D(center, 180, 1.0)
            rotated_image = cv2.warpAffine(rotated_image, matrix, (width, height))

            # Grab image
            with self.lock:
                self.image = rotated_image

            # Stop
            if self.stopped:
                self.stream.close()
                self.raw_capture.close()
                self.camera.close()
                return
