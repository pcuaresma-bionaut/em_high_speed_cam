from vimba import *
import threading
import cv2
import os
from datetime import datetime

class Handler:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.frame_time = 0
        self.frame_times = []

    def __call__(self, cam: Camera, frame: Frame):
        global start_frame_time
        global end_frame_time

        start_frame_time = datetime.now()

        NO_KEY_PRESS_CODE = -1
        key = cv2.waitKey(1)

        if key != NO_KEY_PRESS_CODE:
            self.shutdown_event.set()
            return
        elif frame.get_status() == FrameStatus.Complete:
            end_frame_time = datetime.now()
            self.frame_time = end_frame_time - start_frame_time
            self.frame_times.append(self.frame_time)

            print('{} acquired {}'.format(cam, frame), flush=True)

            msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'

            frame_image = frame.as_opencv_image()
            cv2.imshow(msg.format(cam.get_name()), frame_image)
            directory = os.path.join(os.path.dirname(__file__), "gravity_test_images/")
            os.chdir(directory)
            filename = f"img_{frame.get_id()}.jpg"
            cv2.imwrite(filename, frame_image)

        cam.queue_frame(frame)

def frame_handler(cam, frame):
    print('{} acquired {}'.format(cam, frame), flush=True)
    cam.queue_frame(frame)

def main():
    global start_frame_time
    global end_frame_time

    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            handler = Handler()
            try:
                cam.start_streaming(handler=handler, buffer_count=10)
                handler.shutdown_event.wait()

                print_frame_time_stuff(handler)
            finally:
                cam.stop_streaming()
            

def print_frame_time_stuff(handler):
    frame_times_in_seconds = [time.total_seconds() for time in handler.frame_times]
    [print(str(time)) for time in frame_times_in_seconds]
    total_time_in_seconds = sum(frame_times_in_seconds)
    print(f"Total time (s): {total_time_in_seconds}")
    num_frames_collected = len(frame_times_in_seconds)
    print(f"Number of frames collected: {num_frames_collected}")
    average_time_in_seconds = total_time_in_seconds / num_frames_collected
    print(f"Average time (s): {average_time_in_seconds}")

    print(f"Frequency (1 / AverageTime): {1/average_time_in_seconds}")
            

def print_camera_features(cam):
    features = cam.get_all_features()
    for feature in features:
        print(feature)

if __name__ == '__main__':
    main()