import pytest
import subprocess
from multiprocessing import Process

import sys
sys.path.append("../em_high_speed_cam")
print(sys.path)
from async_fps_testing import *

CAM_ID = "DEV_1AB228000FA4"
IS_CAM_CONNECTED = True

"""
TODO:
- make a generic "test__prints_to_stdout()" function
"""

class TestMain:
    """
    test preamble is printed
    test cam_id gets set
    test cam_id gets set to expected value from parse_args
    test parse args?
    test init_cam_max_fps
        test given valid camera object, its:
            UserSetDefault attribute is set to "UserSet1"
            
            ExposureMode attribute is set to "Timed"
            ExposureMode printed to stdout

            ExposureTime attribute is set to 500
            ExposureTime printed to stdout

            TriggerMode attribute is set to "Off"
            TriggerMode printed to stdout

            AcquisitionFrameRateMode attribute is set to "Basic"
            AcquisitionFrameRateMode printed to stdout

            AcquisitionMode attribute is set to "Continuous"
            AcquisitionMode printed to stdout

            AcquisitionFrameRate attribute is set to 500
            AcquisitionFrameRate printed to stdout

            TriggerSelector attribute is set to "AcquisitionStart"
            TriggerSelector printed to stdout

            TriggerMode attribute is set to "On"
            TriggerMode printed to stdout

            TriggerSource attribute is set to "Software"
            TriggerSource printed to stdout

            TriggerActivation attribute is set to "AnyEdge"
            TriggerActivation printed to stdout

            AcquisitionStart --?

            AcquisitionStatus printed to stdout
            AcquisitionStatusSelector printed to stdout

        [print(feature, "\n") for feature in self.camera.get_all_features()]
    """
@pytest.mark.skipif(IS_CAM_CONNECTED == False, reason="This test relies on the camera being connected.")
class TestInitCamMaxFPS:
    def setup_class(self):
        self.vimba = Vimba.get_instance()
        self.camera = get_camera(None)
        with self.vimba:
            with self.camera:
                init_cam_max_fps(self.camera)
                
    def test_default_user_set_is_expected_value(self):
        with self.vimba:
            with self.camera:
                user_set_default = self.camera.get_feature_by_name('UserSetDefault').get()
                assert str(user_set_default) == "UserSet1"
    
    def test_exposure_mode_attribute_set_to_expected_value(self):
        with self.vimba:
            with self.camera:
                exposure_mode = self.camera.ExposureMode.get()
                # exposure_mode = self.camera.get_feature_by_name("ExposureMode").get()
                assert str(exposure_mode) == "Timed"

    def test_exposure_mode_printed_to_stdout(self):
        pass
    
    def test_exposure_time_attribute_set_to_expected_value(self):
        with self.vimba:
            with self.camera:
                exposure_time = self.camera.ExposureTime.get()
                # exposure_time = self.camera.get_feature_by_name("ExposureTime").get()
                assert pytest.approx(exposure_time, 1e-4) == 500.

    def test_exposure_time_printed_to_stdout(self):
        pass
    
    def test_trigger_mode_attribute_set_to_expected_value(self):
        with self.vimba:
            with self.camera:
                trigger_mode = self.camera.TriggerMode.get()
                # trigger_mode = self.camera.get_feature_by_name("TriggerMode").get()
                assert str(trigger_mode) == "Off"

    def test_trigger_mode_printed_to_stdout(self):
        pass

    def test_acquisition_frame_rate_mode_set_to_expected_value(self):
        with self.vimba:
            with self.camera:
                acquisition_frame_rate_mode = self.camera.AcquisitionFrameRateMode.get()
                assert str(acquisition_frame_rate_mode) == "Basic"
    
    def test_acquisition_frame_rate_mode_printed_to_stdout(self):
        pass
    
    def test_acquisition_mode_attribute_set_to_expected_value(self):
        with self.vimba:
            with self.camera:
                acquisition_mode = self.camera.AcquisitionMode.get()
                assert str(acquisition_mode) == "Continuous"
    
    def test_acquisition_mode_printed_to_stdout(self):
        pass

    def test_acquisition_frame_rate_attribute_set_to_expected_value(self):
        with self.vimba:
            with self.camera:
                acquisition_frame_rate = self.camera.AcquisitionFrameRate.get()
                assert pytest.approx(acquisition_frame_rate, 1e-6) == 500.
    
    def test_acquisition_frame_rate_printed_to_stdout(self):
        pass
    

        """
        test given valid camera object, its:
            TriggerSelector attribute is set to "AcquisitionStart"
            TriggerSelector printed to stdout

            TriggerMode attribute is set to "On"
            TriggerMode printed to stdout

            TriggerSource attribute is set to "Software"
            TriggerSource printed to stdout

            TriggerActivation attribute is set to "AnyEdge"
            TriggerActivation printed to stdout

            AcquisitionStart --?

            AcquisitionStatus printed to stdout
            AcquisitionStatusSelector printed to stdout"""


def assert_stdout_matches_expected_output_for_command(command, expected_output):
    command_subprocess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, text=True)
    first_line_without_newline = str(command_subprocess.stdout.readline()[:-1])
    assert first_line_without_newline == expected_output

            

@pytest.mark.skipif(IS_CAM_CONNECTED == False, reason="This test relies on the camera being connected.")
class TestAsyncOGWithCameraConnected:
    def test_given_none_as_input_get_camera_returns_a_camera(self):
        cam = get_camera(None)
        assert cam is not None

    def test_given_camera_id_get_camera_returns_camera_with_expected_id(self):
        cam = get_camera(CAM_ID)
        assert cam.get_id() == CAM_ID
    
    def test_given_unexpected_camera_id_get_camera_prints_expected_abort_message_to_stdout(self):
        command = "python3 -c 'import async_og; async_og.get_camera(\"wrong_cam_id\")'"
        expected_output = "Failed to access Camera \'wrong_cam_id\'. Abort."
        assert_stdout_matches_expected_output_for_command(command, expected_output)


@pytest.mark.skipif(IS_CAM_CONNECTED == True, reason="This test relies on the camera not being connected.")
class TestAsyncOGNoCameraConnected:
    def setup_class(self):
        self.command_for_running_get_camera_with_none = "python3 -c 'import async_og; async_og.get_camera(None)'"
        self.subprocess_get_camera = subprocess.Popen(self.command_for_running_get_camera_with_none, shell=True, stdout=subprocess.PIPE, text=True)

        self.command = "python3 -c 'import async_og; async_og.get_camera(None)'"

    def test_get_camera_prints_expected_abort_msg_to_stdout_given_none(self):
        expected_output = "No Cameras accessible. Abort."
        assert_stdout_matches_expected_output_for_command(self.command, expected_output)

    def test_get_camera_exits_with_code_1_given_none(self):
        self.subprocess_get_camera.communicate()
        assert self.subprocess_get_camera.returncode == 1
