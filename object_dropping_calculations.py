import numpy as np

distance_in_mm = 1000
num_frames = 170 - 132

time_in_ms = np.sqrt(distance_in_mm / (0.0049))

fps = num_frames * 1000 / time_in_ms

print(f"FPS: {fps}")