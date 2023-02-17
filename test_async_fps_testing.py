import pytest
from async_fps_testing import *
import subprocess as sp
from multiprocessing import Process

CAM_ID = "DEV_1AB228000FA4"
IS_CAM_CONNECTED = False

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

    """

class TestAsyncOGWithCameraConnected:
    @pytest.mark.skipif(IS_CAM_CONNECTED != True, reason="This test relies on the camera being connected.")
    def test_given_none_as_input_get_camera_returns_a_camera(self):
        cam = get_camera(None)
        assert cam is not None

    @pytest.mark.skipif(IS_CAM_CONNECTED != True, reason="This test relies on the camera being connected.")
    def test_given_camera_id_get_camera_returns_camera_with_expected_id(self):
        cam = get_camera(CAM_ID)
        assert cam.get_id() == CAM_ID

    @pytest.mark.skipif(IS_CAM_CONNECTED != True, reason="This test relies on the camera being connected.")
    def test_given_unexpected_camera_id_get_camera_prints_expected_abort_message_to_stdout(self):
        self.command_for_running_get_camera_with_wrong_camera_id = "python3 -c 'import async_og; async_og.get_camera(\"wrong_cam_id\")'"
        self.subprocess_get_camera = sp.Popen(self.command_for_running_get_camera_with_wrong_camera_id, shell=True, stdout=sp.PIPE, text=True)
        first_line_without_newline = str(self.subprocess_get_camera.stdout.readline()[:-1])
        assert first_line_without_newline == "Failed to access Camera \'wrong_cam_id\'. Abort."


class TestAsyncOGNoCameraConnected:
    def setup_class(self):
        self.command_for_running_get_camera_with_none = "python3 -c 'import async_og; async_og.get_camera(None)'"
        self.subprocess_get_camera = sp.Popen(self.command_for_running_get_camera_with_none, shell=True, stdout=sp.PIPE, text=True)
    
    @pytest.mark.skipif(IS_CAM_CONNECTED == True, reason="This test relies on the camera not being connected.")
    def test_get_camera_prints_to_stdout_given_none(self):
        assert self.subprocess_get_camera.stdout != ""

    @pytest.mark.skipif(IS_CAM_CONNECTED == True, reason="This test relies on the camera not being connected.")
    def test_get_camera_prints_expected_abort_msg_to_stdout_given_none(self):
        first_line_without_newline = str(self.subprocess_get_camera.stdout.readline()[:-1])
        assert first_line_without_newline == "No Cameras accessible. Abort."

    @pytest.mark.skipif(IS_CAM_CONNECTED == True, reason="This test relies on the camera not being connected.")
    def test_get_camera_exits_with_code_1_given_none(self):
        self.subprocess_get_camera.communicate()
        assert self.subprocess_get_camera.returncode == 1
