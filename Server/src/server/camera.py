from threading import Thread
from picamera.array import PiRGBArray
from picamera import PiCamera


class Camera(object):
    stopped = False
    image = None
    camera = None
    raw_capture = None
    stream = None

    def start(self, resolution=(640, 480), framerate=32):
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
        return self.image

    def update(self):
        """
        Grabs next image from camera.
        """
        for f in self.stream:
            self.image = f.array
            self.raw_capture.truncate(0)

            # Stop
            if self.stopped:
                self.stream.close()
                self.raw_capture.close()
                self.camera.close()
                return
