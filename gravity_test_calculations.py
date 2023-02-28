import numpy as np

distance_in_mm = 140
num_frames = 3050 - 2955

time_in_ms = np.sqrt(distance_in_mm / (0.0049))

fps = num_frames * 1000 / time_in_ms

print(f"FPS: {fps}")