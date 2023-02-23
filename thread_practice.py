from vimba import *
import threading
import cv2
from datetime import datetime

class Handler:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.frame_time = 0
        self.frame_times = []

    def __call__(self, cam: Camera, frame: Frame):
        NO_KEY_PRESS_CODE = -1
        key = cv2.waitKey(1)
        if key != NO_KEY_PRESS_CODE:
            self.shutdown_event.set()
            return
        elif frame.get_status() == FrameStatus.Complete:
            self.frame_time = datetime.now() - start_time
            self.frame_times.append(self.frame_time)
            print('{} acquired {}'.format(cam, frame), flush=True)

            msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'
            cv2.imshow(msg.format(cam.get_name()), frame.as_opencv_image())

        cam.queue_frame(frame)

def frame_handler(cam, frame):
    print('{} acquired {}'.format(cam, frame), flush=True)
    cam.queue_frame(frame)

def main():
    global start_time

    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            handler = Handler()
            try:
                start_time = datetime.now()
                cam.start_streaming(handler=handler, buffer_count=10)
                handler.shutdown_event.wait()

                average_time = handler.frame_times
                [print(str(avg)) for avg in average_time]
            finally:
                cam.stop_streaming()
            
            

def print_all_features(cam):
    features = cam.get_all_features()
    for feature in features:
        print(feature)

if __name__ == '__main__':
    main()