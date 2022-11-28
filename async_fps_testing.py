
"""BSD 2-Clause License

Copyright (c) 2019, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

THE SOFTWARE IS PRELIMINARY AND STILL IN TESTING AND VERIFICATION PHASE AND
IS PROVIDED ON AN â€œAS ISâ€ AND â€œAS AVAILABLEâ€ BASIS AND IS BELIEVED TO CONTAIN DEFECTS.
A PRIMARY PURPOSE OF THIS EARLY ACCESS IS TO OBTAIN FEEDBACK ON PERFORMANCE AND
THE IDENTIFICATION OF DEFECT SOFTWARE, HARDWARE AND DOCUMENTATION.
"""

import threading
import cv2
from typing import Optional
import sys
from sys import argv
from datetime import datetime
import statistics as stat
import time

sys.path.append('C:/Program Files/Allied Vision/Vimba_6.0/VimbaPython/Source')
# sys.path.append('/mnt/c/Users/Public/Documents/Allied Vision/Vimba_6.0/VimbaPython_Source/vimba')
sys.path
from vimba import *
# for path in sys.path:ls
#     print(path)
# import pymba as vimba
image_name = []



def resize(img_array, align_mode):
    _height = len(img_array[0])
    _width = len(img_array[0][0])
    for i in range(1, len(img_array)):
        img = img_array[i]
        height = len(img)
        width = len(img[0])
        if align_mode == 'smallest':
            if height < _height:
                _height = height
            if width < _width:
                _width = width
        else:
            if height > _height:
                _height = height
            if width > _width:
                _width = width

    for i in range(0, len(img_array)):
        img1 = cv2.resize(img_array[i], (_width, _height), interpolation=cv2.INTER_CUBIC)
        img_array[i] = img1

    return img_array, (_width, _height)

def images_to_video(images, video_file):
    # make all image size is same
    img_array = []
    for i in images:
        img = cv2.imread(i)
        if img is None:
            continue
        img_array.append(img)
    img_array, size = resize(img_array, 'largest')
    fps = 1
    out = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'DVIX'), fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()


def print_preamble():
    print('///////////////////////////////////////////////////////')
    print('/// Vimba API Asynchronous Grab with OpenCV Example ///')
    print('///////////////////////////////////////////////////////\n')


def print_usage():
    print('Usage:')
    print('    python asynchronous_grab_opencv.py [camera_id]')
    print('    python asynchronous_grab_opencv.py [/h] [-h]')
    print()
    print('Parameters:')
    print('    camera_id   ID of the camera to use (using first camera if not specified)')
    print()


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')

    if usage:
        print_usage()

    sys.exit(return_code)


def parse_args() -> Optional[str]:
    args = sys.argv[1:]
    argc = len(args)

    for arg in args:
        if arg in ('/h', '-h'):
            print_usage()
            sys.exit(0)

    if argc > 1:
        abort(reason="Invalid number of arguments. Abort.",
              return_code=2, usage=True)

    return None if argc == 0 else args[0]


def get_camera(camera_id: Optional[str]) -> Camera:
    with Vimba.get_instance() as vimba:
        if camera_id:
            try:
                return vimba.get_camera_by_id(camera_id)

            except VimbaCameraError:
                abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))

        else:
            cams = vimba.get_all_cameras()
            if not cams:
                abort('No Cameras accessible. Abort.')

            return cams[0]

def init_cam_max_fps(cam: Camera):
    with cam:
        
        try:
            cam.UserSetDefault.set('UserSet1')
            cam.ExposureMode.set('Timed')
            print(f"{cam.ExposureMode.get()}")
            cam.ExposureTime.set(500)
            print(f"{cam.ExposureTime.get()}")
            cam.TriggerMode.set('Off')
            print(f"{cam.TriggerMode.get()}")

            cam.AcquisitionFrameRateMode.set('Basic')
            print(f"{cam.AcquisitionFrameRateMode.get()}")

            cam.AcquisitionMode.set('Continuous')
            print(f"{cam.AcquisitionMode.get()}")

            cam.AcquisitionFrameRate.set(500)
            print(f"{cam.AcquisitionFrameRate.get()}")

            cam.TriggerSelector.set('AcquisitionStart')
            print(f"{cam.TriggerSelector.get()}")
            
            cam.TriggerMode.set('On')
            print(f"{cam.TriggerMode.get()}")
            
            cam.TriggerSource.set('Software')
            print(f"{cam.TriggerSource.get()}")
            
            cam.TriggerActivation.set('AnyEdge')
            print(f"{cam.TriggerActivation.get()}")
            
            cam.AcquisitionStart.run()
            print(f"{cam.AcquisitionStatus.get()}")
            # cam.AcquisitionStatusSelector.set("AcquisitionActive")
            print(f"{cam.AcquisitionStatusSelector.get()}")

            #cam.TriggerMode.set('On')
            #print(f"{cam.TriggerMode.get()}")
            cam.TriggerSoftware.run()
            print(f"{cam.AcquisitionStatusSelector.get()}")
            
        except (AttributeError, VimbaFeatureError):
            print("Error Setting Custom Values")
            pass 
            
          # Enable white balancing if camera supports it
        # try:
        #     cam.BalanceWhiteAuto.set('Continuous')

        # except (AttributeError, VimbaFeatureError):
        #     print("Error White Auto")
        #     pass       

        # Query available, open_cv compatible pixel formats
        # prefer color formats over monochrome formats
        # cv_fmts = intersect_pixel_formats(
        #     cam.get_pixel_formats(), OPENCV_PIXEL_FORMATS)
        # color_fmts = intersect_pixel_formats(cv_fmts, COLOR_PIXEL_FORMATS)

        # if color_fmts:
        #     cam.set_pixel_format(color_fmts[0])

        # else:
        #     mono_fmts = intersect_pixel_formats(cv_fmts, MONO_PIXEL_FORMATS)

        #     if mono_fmts:
        #         cam.set_pixel_format(mono_fmts[0])

        #     else:
        #         abort('Camera does not support a OpenCV compatible format natively. Abort')
startTs = None
finishTs = None
class Handler:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.count = 0
        self.ts = []
        self.ts_last = None
        self.key = 0

    def __call__(self, cam: Camera, frame: Frame):

        if self.ts_last != None:
            self.ts.append((datetime.now() - self.ts_last).total_seconds())
        self.ts_last = datetime.now()

        if frame.get_status() == FrameStatus.Complete:

            file_name = '{}frame{}.jpg'.format(cam, frame)
            cv2.imwrite(file_name, frame.as_opencv_image())
            image_name.append(file_name)
            self.count +=1
            
        if self.count > 40000:
            cam.AcquisitionAbort.run()
            self.shutdown_event.set()
            timestamp_str = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")
            images_to_video(images=image_name, video_file=f"video_{timestamp_str}.mp4")
            #images_to_video(images=image_name, video_file=sys.argv[1])
        
        
        cam.queue_frame(frame)

def process(cam: Camera, hndl: Handler):
    try:
        cam.start_streaming(handler=hndl, buffer_count=10)
        hndl.shutdown_event.wait()
        
    finally:
        cam.stop_streaming()

def exitProgram(cam: Camera, hndl: Handler):
    global startTs
    global finishTs
    finishTs = datetime.now()
    print("Stopped recording.")
    cam.AcquisitionAbort.run()
    cam.stop_streaming()
    print(f"Avg time: {stat.mean(hndl.ts)}")
    p = stat.quantiles(hndl.ts, n=10)
    print(f"High time: {p[8]}")
    print(f"Low time: {p[0]}")
    print(f"Capture time: {(finishTs-startTs).total_seconds()}")
    print(f"Number of Frames: {len(image_name)}")
    timestamp_str = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")
    images_to_video(images=image_name, video_file=f"video_{timestamp_str}.mp4")
    hndl.shutdown_event.set()

def main():
    global startTs
    global finishTs
    print_preamble()
    cam_id = parse_args()

    with Vimba.get_instance():
        with get_camera(cam_id) as cam:

            # Start Streaming, wait for five seconds, stop streaming
            init_cam_max_fps(cam)
            #setup_camera(cam)
            handler = Handler()
            try:
                 startTs = datetime.now()
                 threading.Thread(target=process, args=[cam, handler]).start()
                 while True:
                    time.sleep(1)
                    continue
            except (KeyboardInterrupt):
                exitProgram(cam, hndl=handler)
            finally:
                cam.stop_streaming()

            # try:
            #     # Start Streaming with a custom a buffer of 10 Frames (defaults to 5)
            #     cam.start_streaming(handler=handler, buffer_count=10)
            #     handler.shutdown_event.wait()

            # finally:
            #     cam.stop_streaming()


if __name__ == '__main__':
    main()
