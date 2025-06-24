import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from skimage.feature import peak_local_max
from scipy.ndimage import gaussian_filter

# Load data and dead pixels
data = np.load('C:/software/AMBpy_export.npy')
dead_pixels = pd.read_csv('C:/software/AMIGOpy/dead_pixels.csv', header=None, names=['x', 'y'])

def replace_dead_pixels(data, dead_pixels):
    for frame_index in range(data.shape[0]):
        frame = data[frame_index, :, :]
        for index, row in dead_pixels.iterrows():
            x, y = row['x'], row['y']
            if 0 <= x < frame.shape[0] and 0 <= y < frame.shape[1]:  # Ensure the pixel is within the frame
                x_min, x_max = max(x-1, 0), min(x+2, frame.shape[0])
                y_min, y_max = max(y-1, 0), min(y+2, frame.shape[1])
                neighborhood = frame[x_min:x_max, y_min:y_max]
                valid_neighbors = np.ma.masked_array(neighborhood, mask=False)
                valid_neighbors.mask[(x-x_min):(x-x_min+1), (y-y_min):(y-y_min+1)] = True
                if np.ma.count(valid_neighbors) > 0:
                    mean_value = np.ma.mean(valid_neighbors)
                    frame[x, y] = mean_value
        data[frame_index, :, :] = frame

replace_dead_pixels(data, dead_pixels)

# Adjust the data for visualization
data = data.astype(np.float32)
data = (65500 - data) / 65500
data = np.power(data, 4)
data = np.flip(data, axis=1)
# Apply Gaussian blur to each frame independently
for i in range(data.shape[0]):
    data[i, :, :] = gaussian_filter(data[i, :, :], sigma=5)  # Adjust sigma as needed for each frame

    # Find peaks in the processed frame
    peaks = peak_local_max(data[i, :, :], min_distance=30, threshold_rel=0.1, exclude_border=50)




    # Sort peaks by x-coordinate first to facilitate grouping
    peaks_sorted = peaks[np.argsort(peaks[:, 1])]


    # Apply specific row exclusions based on frame ranges
    if i < 3:
        peaks_filtered = peaks_sorted[(peaks_sorted[:, 0] >= 200) & (peaks_sorted[:, 0] <= 650)]
    elif 3 <= i < 6:
        peaks_filtered = peaks_sorted[(peaks_sorted[:, 0] >= 280) & (peaks_sorted[:, 0] <= 580)]
    elif 6 <= i < 9:
        peaks_filtered = peaks_sorted[(peaks_sorted[:, 0] >= 300) & (peaks_sorted[:, 0] <= 550)]

    # Group peaks dynamically based on the actual starting positions
    grouped_peaks = []
    j = 0
    while j < len(peaks_filtered):
        start_col = peaks_filtered[j, 1]
        end_col = start_col + 30
        group = []
        while j < len(peaks_filtered) and peaks_filtered[j, 1] < end_col:
            group.append(peaks_filtered[j])
            j += 1
        grouped_peaks.extend(sorted(group, key=lambda x: x[0]))  # Sort group by y-coordinate


    # Scale the coordinates by 0.4
    peaks_scaled = np.array(grouped_peaks) * 0.45
    peaks_px     = np.array(grouped_peaks)
    # Prepare to save the coordinates to CSV with ID, X, Y order
    peak_coords = pd.DataFrame(peaks_scaled, columns=['Y', 'X'])  # Create a DataFrame with scaled peak coordinates
    if i==0:
        peak_coords['ID'] = range(36,36+len(peak_coords))  # Assign ID numbers to each peak sorted
    elif i==1:
        peak_coords['ID'] = range(30,30+len(peak_coords))  # Assign ID numbers to each peak sorted
    elif i==2:
        peak_coords['ID'] = range(23,23+len(peak_coords))  # Assign ID numbers to each peak sorted
    elif i==3:
        peak_coords['ID'] = range(27,27+len(peak_coords))  # Assign ID numbers to each peak sorted
    elif i==4:
        peak_coords['ID'] = range(23,23+len(peak_coords))  # Assign ID numbers to each peak sorted
    elif i==5:
        peak_coords['ID'] = range(19,19+len(peak_coords))  # Assign ID numbers to each peak sorted elif i==1:
    elif i==6:
        peak_coords['ID'] = range(20,20+len(peak_coords))  # Assign ID numbers to each peak sorted
    elif i==7:
        peak_coords['ID'] = range(19,19+len(peak_coords))  # Assign ID numbers to each peak sorted
    elif i==8:
        peak_coords['ID'] = range(16,16+len(peak_coords))  # Assign ID numbers to each peak sorted
    peak_coords = peak_coords[['ID', 'X', 'Y']]  # Reorder columns as ID, X, Y
    
    peaks2vtk_coord = peak_coords.copy()
    # Invert X values (you may need to adjust for the actual dimensions)
    peaks2vtk_coord['Y'] = -peaks2vtk_coord['Y'] + data.shape[1]*0.45  # Adjusting for the maximum to keep coordinates positive
    # Save peak coordinates to CSV
    peaks2vtk_coord.to_csv(f'C:/software/peaks_frame_{i}.csv', index=False)

    # Plot the frame with peak markers
    fig, ax = plt.subplots()
    ax.imshow(data[i, :, :], interpolation='nearest', cmap='gray')
    ax.scatter(peaks_px [:, 1], peaks_px [:, 0], color='r', s=2)  # Mark the peaks
    # Label each peak with its ID from the DataFrame
    for idx, row in peak_coords.iterrows():
       ax.text(int(row['X']/0.45), int(row['Y']/0.45), str(row['ID']), color='yellow', fontsize=8)  # Label each peak with its ID from the DataFrame

    # Save the plot to a PNG file
    plt.savefig(f'C:/software/frame_{i}.png')
    plt.close(fig)  # Close the plot to free up memory