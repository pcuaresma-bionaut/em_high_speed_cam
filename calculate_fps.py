from vimba import *
import cv2
import os
import threading
import shutil
import time
from datetime import datetime
import numpy as np

"""
TODO:
- output folder name and date
    - default current date
- adjustable/viewable frame rate
"""

OUTPUT_STR = "output"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), OUTPUT_STR + "/")
VIDEO_NAME = OUTPUT_STR + "_video.avi"
FILE_NAME = "{file}.jpg" 
FPS = 475

class FrameHandler:
    def __init__(self):
        # Video/Streaming Fields
        self.shutdown_event = threading.Event()

        try:
            os.makedirs(OUTPUT_DIR)
        except FileExistsError:
            # Directory already exists
            pass

        delete_all_files_in(OUTPUT_DIR)

        # Timing/Frame Rate Fields
        self.timestamps = []

    def handle_frame(self, cam, frame):
        self.timestamps.append(frame.get_timestamp())

        print(f"{cam} acquired {frame}", flush=True)

        msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'

        frame_image = frame.as_opencv_image()
        cv2.imshow(msg.format(cam.get_name()), frame_image)

        os.chdir(OUTPUT_DIR)
        filename = f"img_{frame.get_id()}.jpg"
        cv2.imwrite(filename, frame_image)

    def __call__(self, cam: Camera, frame: Frame):
        """A callback function that is called for every frame received from the camera."""
        global last_time
        current_time = time.monotonic()

        NO_KEY_PRESSED_CODE = -1
        key = cv2.waitKey(1)

        stop_condition = (key != NO_KEY_PRESSED_CODE)
        frame_done = (frame.get_status() == FrameStatus.Complete)

        if stop_condition:
            self.shutdown_event.set()
            return
        elif frame_done:
            self.handle_frame(cam, frame)

        cam.queue_frame(frame)

def setup_camera(camera):
    camera.load_settings("settings_550fps.xml", PersistType.All)

def delete_all_files_in(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def main():
    global start_frame_time
    global end_frame_time

    global last_time
    
    last_time = time.monotonic()
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            setup_camera(cam)

            handler = FrameHandler()
            try:
                start = datetime.now()
                cam.start_streaming(handler=handler, buffer_count=10)
                handler.shutdown_event.wait()

            finally:
                cam.stop_streaming()
                end = datetime.now()
    
    print(f"Total time streaming: {(end-start).total_seconds()}")

    print_frame_rate_calculated_using_vimba_timestamps(handler)

    write_frames_to_video()

def write_frames_to_video():
    images = [img for img in os.listdir(OUTPUT_DIR) if img.endswith(".jpg")]
    images.sort()
    frame = cv2.imread(os.path.join(OUTPUT_DIR, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(VIDEO_NAME, 0, FPS, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(OUTPUT_DIR, image)))

    cv2.destroyAllWindows()
    video.release()
        
def calculate_frame_rate(time_diffs):
    """
    Input: Array of time differences between frames captured
    Output: The frame rate in frames per second
    """
    return 1/np.mean(time_diffs)

def print_frame_rate_calculated_using_vimba_timestamps(handler):
    diffs= []
    for i in range(len(handler.timestamps)-1):
        diffs.append(handler.timestamps[i+1]/1e9 - handler.timestamps[i]/1e9)

    print(f"Average frame rate (fps) using the frames' timestamps: {calculate_frame_rate(diffs)}")

def print_camera_features(cam):
    features = cam.get_all_features()
    for feature in features:
        print(feature)

if __name__ == '__main__':
    main()

