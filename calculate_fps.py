from vimba import *
import threading
import cv2
import os
import shutil
from datetime import datetime

class Handler:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.frame_time = 0
        self.frame_times = []
        self.directory = os.path.join(os.path.dirname(__file__), "gravity_test_images/")
        delete_all_files_in(self.directory)

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

            os.chdir(self.directory)
            filename = f"img_{frame.get_id()}.jpg"
            cv2.imwrite(filename, frame_image)

        cam.queue_frame(frame)

def setup_camera(camera, vimba):
    # Set the acquisition mode to continuous
    camera.AcquisitionMode = 'Continuous'

    # Set the frame rate to 500 fps
    camera.AcquisitionFrameRateAbs = 500

    # Set the pixel format to monochrome 8-bit
    camera.PixelFormat = 'Mono8'

    # Set the exposure time to 1 ms
    camera.ExposureTimeAbs = 10000

    # # Start the capture engine
    camera.startCapture()

    # # Wait for 10 seconds
    vimba.wait(10000)

    # # Stop the capture engine
    camera.stopCapture()

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

def frame_handler(cam, frame):
    print('{} acquired {}'.format(cam, frame), flush=True)
    cam.queue_frame(frame)

def main():
    global start_frame_time
    global end_frame_time

    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            # Set the acquisition mode to continuous
            cam.AcquisitionMode = 'Continuous'

            # Set the frame rate to 500 fps
            cam.AcquisitionFrameRateAbs = 500

            # Set the pixel format to monochrome 8-bit
            cam.PixelFormat = 'Mono8'

            # Set the exposure time to 1 ms
            cam.ExposureTimeAbs = 12000


            handler = Handler()
            try:
                start = datetime.now()
                cam.start_streaming(handler=handler, buffer_count=10)
                handler.shutdown_event.wait()

                print_frame_time_stuff(handler)
            finally:
                cam.stop_streaming()
                end = datetime.now()
    
    print(f"Total time streaming: {(end-start).total_seconds()}")
                
        

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