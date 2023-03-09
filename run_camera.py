from vimba import *
import cv2
import os
import threading
import shutil
import time
from datetime import datetime
import numpy as np
import time
import sys
import argparse
import getopt

"""
TODO:
- output folder name and date
    - default current date
- adjustable/viewable frame rate
- automatically exclude unnecessary frames at beginning and end when making video
- save output to one file but with adjustable names
    - AND ASK TO OVERRIDE IF SAME NAME IS CHOSEN
- add notes after video is taken


> output/
    > name-year-month-day/
        > images/
            > name_frame_frame#
        > name_video.avi
    >name2-year-month-day/
        > images/
            > name_frame_frame#
        > name_video.avi
"""

OUTPUT_STR = "test_output"

def configure_save_settings():
    args = get_parsed_arguments()
    OUTPUT_STR = args.file_string
    DELETE_FRAMES = args.video_only
    print(f"file string? {OUTPUT_STR}")
    print(f"delete frames? {DELETE_FRAMES}")

def get_parsed_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_string", default="test_output", help="string to be used in output directory name, output video file name, and output frame image file names. Purpose: to identify the camera run the output originates from.")
    parser.add_argument("-v", "--video-only", action='store_true', default=False, help="if true, stores the video only (no frames); defaults to False")
    args = parser.parse_args(sys.argv[1:])
    return args

timestr = time.strftime("%Y%m%d-%H%M%S")
    
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), OUTPUT_STR + "/")
VIDEO_NAME = OUTPUT_STR + "_video.avi"
FILE_NAME = OUTPUT_STR + "_image_{:0>6}.jpg" 
FPS = 475

def prepare_output_folder():
    try:
        os.makedirs(OUTPUT_DIR)
    except FileExistsError:
        delete_all_files_in(OUTPUT_DIR)
        pass

class ImageFunctions:
    def show(frame_image, cam):
        msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'
        cv2.imshow(msg.format(cam.get_name()), frame_image)

    def show_and_save(frame, cam):
        frame_image = frame.as_opencv_image()
        ImageFunctions.show(frame_image,cam)

        os.chdir(OUTPUT_DIR)
        cv2.imwrite(FILE_NAME.format(frame.get_id()), frame_image)

class FrameHandler:
    def __init__(self):
        # Video/Streaming Fields
        self.shutdown_event = threading.Event()

        prepare_output_folder()

        # Timing/Frame Rate Fields
        self.timestamps = []

    def handle_frame(self, cam, frame):
        if frame.get_status() == FrameStatus.Complete:
            self.timestamps.append(frame.get_timestamp())
            print(f"{cam} acquired {frame}", flush=True)
            ImageFunctions.show_and_save(frame, cam)

    def __call__(self, cam: Camera, frame: Frame):
        """A callback function that is called for every frame received from the camera."""
        self.wait_for_keypress()
        self.handle_frame(cam, frame)
        cam.queue_frame(frame)

    def wait_for_keypress(self):
        NO_KEY_PRESSED_CODE = -1
        if cv2.waitKey(1) != NO_KEY_PRESSED_CODE:
            self.shutdown_event.set()


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

def write_frames_to_video():
    images = [img for img in os.listdir(OUTPUT_DIR) if img.endswith(".jpg")]
    images.sort()

    frame = cv2.imread(os.path.join(OUTPUT_DIR, images[0]))
    height, width, _ = frame.shape

    video = cv2.VideoWriter(VIDEO_NAME, 0, FPS, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(OUTPUT_DIR, image)))

    cv2.destroyAllWindows()
    video.release()
    
    if DELETE_FRAMES:
        for f in os.listdir(OUTPUT_DIR):
            if not f.endswith(".jpg"):
                continue
            os.remove(os.path.join(mydir, f))
                
def calculate_frame_rate(time_diffs):
    """
    Input: Array of time differences between frames captured
    Output: The frame rate in frames per second
    """
    return 1/np.mean(time_diffs)

def print_frame_rate_calculated_using_vimba_timestamps(handler):
    diffs= []
    for i in range(len(handler.timestamps)-1):
        diffs.append((handler.timestamps[i+1] - handler.timestamps[i])*1e-9)

    print(f"Average frame rate (fps) using the frames' timestamps: {calculate_frame_rate(diffs)}")

def print_camera_features(cam):
    features = cam.get_all_features()
    for feature in features:
        print(feature)

def main():
    configure_save_settings()

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
    
    print(f"Total time streaming: {(end-start).total_seconds()} seconds")

    print_frame_rate_calculated_using_vimba_timestamps(handler)
    write_frames_to_video()

if __name__ == '__main__':
    main()

