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
import logging

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

FPS = 475

class IOStuff:
    def __init__(self):
        self.output_str, self.delete_frames = self.configure_save_settings()
        self.output_dir = self.prepare_output_folder()
        self.video_name = self.output_str + "_video.avi"
        self.file_name = self.output_str + "_image_{:0>6}.jpg"
        
    def configure_save_settings(self):
        args = self.get_parsed_arguments()
        return args.output_file_string, args.video_only

    def get_parsed_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("output_file_string", default="test_output", help="string to be used in output directory name, output video file name, and output frame image file names. Purpose: to identify the camera run the output originates from. e.g., 'output1'")
        parser.add_argument("-v", "--video-only", action='store_true', default=False, help="if true, stores the video only (no frames); defaults to False")
        args = parser.parse_args(sys.argv[1:])
        return args

    def prepare_output_folder(self):
        try:
            output_folder = os.path.join(os.path.dirname(__file__), self.output_str + "/")
            os.makedirs(output_folder)
        except FileExistsError:
            sys.stdout.write(f"This action will delete the folder \n\t{output_folder} \nand its contents. Press 'y' to continue or 'n' to cancel: ")
            answer = input().lower()
            if answer == 'y':
                self.delete_all_files_in(output_folder)
                pass
            elif answer == 'n':
                sys.exit()
        return output_folder

    def delete_all_files_in(self, folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def write_frames_to_video(self):
        logging.info(f"Saving frames as video to: {self.output_str}/...")
        images = [img for img in os.listdir(self.output_dir) if img.endswith(".jpg")]
        images.sort()

        frame = cv2.imread(os.path.join(self.output_dir, images[0]))
        height, width, _ = frame.shape

        video = cv2.VideoWriter(self.video_name, 0, FPS, (width,height))

        for image in images:
            video.write(cv2.imread(os.path.join(self.output_dir, image)))

        cv2.destroyAllWindows()
        video.release()
        
        if self.delete_frames:
            logging.info("Deleting frames...")
            for f in os.listdir(self.output_dir):
                if not f.endswith(".jpg"):
                    continue
                os.remove(os.path.join(self.output_dir, f))
        logging.info("Done.")

class ImageFunctions:
    def show(frame_image, cam):
        msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'
        cv2.imshow(msg.format(cam.get_name()), frame_image)

    def show_and_save(frame, cam, io_stuff):
        frame_image = frame.as_opencv_image()
        ImageFunctions.show(frame_image,cam)

        os.chdir(io_stuff.output_dir)
        cv2.imwrite(io_stuff.file_name.format(frame.get_id()), frame_image)

class FrameHandler:
    def __init__(self, io_stuff):
        self.shutdown_event = threading.Event()
        self.timestamps = []
        self.io_stuff = io_stuff

    def handle_frame(self, cam, frame):
        if frame.get_status() == FrameStatus.Complete:
            self.timestamps.append(frame.get_timestamp())
            print(f"{cam} acquired {frame}", flush=True)
            ImageFunctions.show_and_save(frame, cam, self.io_stuff)

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
    logging.getLogger().setLevel(logging.INFO) # Uncomment to enable info-level logging
    io_stuff = IOStuff()

    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            setup_camera(cam)
            handler = FrameHandler(io_stuff)
            try:
                start = datetime.now()
                cam.start_streaming(handler=handler, buffer_count=10)
                handler.shutdown_event.wait()
            finally:
                cam.stop_streaming()
                end = datetime.now()
    
    print(f"Total time streaming: {(end-start).total_seconds()} seconds")

    print_frame_rate_calculated_using_vimba_timestamps(handler)
    io_stuff.write_frames_to_video()

if __name__ == '__main__':
    main()

