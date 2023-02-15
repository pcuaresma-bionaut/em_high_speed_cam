import pytest
from async_og import get_camera

CAM_ID = "DEV_1AB228000FA4"

class TestAsyncOG:
    def test_when_given_none_as_input_get_camera_returns_camera_with_expected_id(self):
        cam = get_camera(None)

        assert cam.get_id() == CAM_ID

    def test_get_camera_returns_camera_with_expected_id(self):
        cam = get_camera(CAM_ID)
        
        assert cam.get_id() == CAM_ID