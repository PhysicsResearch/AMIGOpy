import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pandas as pd
from skimage.feature import peak_local_max
from scipy.ndimage import gaussian_filter

# Load data and dead pixels
data = np.load('C:/Users/gabriel.paivafonseca/Desktop/chan_1_dw_4.npy')
# dead_pixels = pd.read_csv('C:/software/AMIGOpy/dead_pixels.csv', header=None, names=['x', 'y'])

# def replace_dead_pixels(data, dead_pixels):
#     for frame_index in range(data.shape[0]):
#         frame = data[frame_index, :, :]
#         for index, row in dead_pixels.iterrows():
#             x, y = row['x'], row['y']
#             if 0 <= x < frame.shape[0] and 0 <= y < frame.shape[1]:  # Ensure the pixel is within the frame
#                 x_min, x_max = max(x-1, 0), min(x+2, frame.shape[0])
#                 y_min, y_max = max(y-1, 0), min(y+2, frame.shape[1])
#                 neighborhood = frame[x_min:x_max, y_min:y_max]
#                 valid_neighbors = np.ma.masked_array(neighborhood, mask=False)
#                 valid_neighbors.mask[(x-x_min):(x-x_min+1), (y-y_min):(y-y_min+1)] = True
#                 if np.ma.count(valid_neighbors) > 0:
#                     mean_value = np.ma.mean(valid_neighbors)
#                     frame[x, y] = mean_value
#         data[frame_index, :, :] = frame

# replace_dead_pixels(data, dead_pixels)

# Adjust the data for visualization
data = data.astype(np.float32)
data = (65500 - data) / 65500
data = np.power(data, 2)

# Apply Gaussian blur to each frame independently
for i in range(data.shape[0]):
    data[i, :, :] = gaussian_filter(data[i, :, :], sigma=5)  # Adjust sigma as needed for each frame


fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

initial_slice = 5
slice_plot = plt.imshow(data[initial_slice, :, :], interpolation='nearest')

# Slider
ax_slice = plt.axes([0.1, 0.05, 0.65, 0.03])
slice_slider = Slider(ax_slice, 'Slice', 0, data.shape[0] - 1, valinit=initial_slice, valfmt='%0.0f')

# Container for peak markers
peak_markers, = ax.plot([], [], 'r.')

def update(val):
    slice_index = int(slice_slider.val)
    current_frame = data[slice_index, :, :]
    peaks = peak_local_max(current_frame, min_distance=30, threshold_rel=0.1,exclude_border=50)
    
    # Clear previous peaks
    peak_markers.set_data(peaks[:, 1], peaks[:, 0])
    
    slice_plot.set_data(current_frame)
    fig.canvas.draw_idle()

slice_slider.on_changed(update)

plt.show()