import pytest
from async_og import *

CAM_ID = "DEV_1AB228000FA4"

class TestAsyncOGWithCameraConnected:
    def test_given_none_as_input_get_camera_returns_a_camera(self):
        cam = get_camera(None)

        assert cam is not None

    def test_given_camera_id_get_camera_returns_camera_with_expected_id(self):
        cam = get_camera(CAM_ID)

        assert cam.get_id() == CAM_ID


class TestAsyncOGNoCameraConnected:
    def test_get_camera_does_something_still(self):
        cam = get_camera(None)
        pass