import pytest
from async_og import *
import subprocess as sp
from multiprocessing import Process

CAM_ID = "DEV_1AB228000FA4"
IS_CAM_CONNECTED = False

class TestAsyncOGWithCameraConnected:
    @pytest.mark.skipif(IS_CAM_CONNECTED != True, reason="This test relies on the camera being connected.")
    def test_given_none_as_input_get_camera_returns_a_camera(self):
        cam = get_camera(None)
        assert cam is not None

    @pytest.mark.skipif(IS_CAM_CONNECTED != True, reason="This test relies on the camera being connected.")
    def test_given_camera_id_get_camera_returns_camera_with_expected_id(self):
        cam = get_camera(CAM_ID)
        assert cam.get_id() == CAM_ID


class TestAsyncOGNoCameraConnected:
    def setup_class(self):
        self.command_for_running_get_camera = "python3 -c 'import async_og; async_og.get_camera(None)'"
        self.subprocess_get_camera = sp.Popen(self.command_for_running_get_camera, shell=True, stdout=sp.PIPE, text=True)
    
    @pytest.mark.skipif(IS_CAM_CONNECTED == True, reason="This test relies on the camera not being connected.")
    def test_get_camera_prints_to_stdout_given_none(self):
        assert self.subprocess_get_camera.stdout != ""

    @pytest.mark.skipif(IS_CAM_CONNECTED == True, reason="This test relies on the camera not being connected.")
    def test_get_camera_prints_expected_error_msg_to_stdout_given_none(self):
        first_line_without_newline = str(self.subprocess_get_camera.stdout.readline()[:-1])
        assert first_line_without_newline == "No Cameras accessible. Abort."

    @pytest.mark.skipif(IS_CAM_CONNECTED == True, reason="This test relies on the camera not being connected.")
    def test_get_camera_exits_with_code_1_given_none(self):
        self.subprocess_get_camera.communicate()
        assert self.subprocess_get_camera.returncode == 1
