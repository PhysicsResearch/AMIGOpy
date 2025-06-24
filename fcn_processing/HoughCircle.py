import numpy as np
import matplotlib.pyplot as plt
import cv2


def get_settings(self):
    initial_slice = self.Proces_spinbox_01.value()
    final_slice   = self.Proces_spinbox_02.value()
    param1        = self.Proces_spinbox_03.value()
    param2        = self.Proces_spinbox_04.value()
    minRadius     = self.Proces_spinbox_05.value()
    maxRadius     = self.Proces_spinbox_06.value()
    image         = self.display_data[self.current_slice_index[0], :, :]
    detect_circles(image, minRadius, maxRadius, param1, param2)
    
    
def plot_image(image, title):
    plt.figure(figsize=(4, 4))
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.axis('off')

def detect_circles(image, minRadius=5, maxRadius=14, param1=50, param2=30):
    # Ensure the image is a 2D array
    if len(image.shape) > 2:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image

    # Plot the input image
    plot_image(gray_image, 'Input Image')

    # Normalize the image for better contrast
    normalized_image = cv2.normalize(gray_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    
    # Plot the normalized image
    plot_image(normalized_image, 'Normalized Image')

    # Apply a blur to reduce noise
    blurred_image = cv2.GaussianBlur(normalized_image, (9, 9), 0)

    # Plot the blurred image
    plot_image(blurred_image, 'Blurred Image')

    # Invert the image to highlight low intensity (dark) spheres on a light background
    threshold_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 11, 2)

    plot_image(threshold_image, 'Adaptive Thresholded Image')


    # Detect circles using the Hough Circle Transform
    circles = cv2.HoughCircles(
        gray_image,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=minRadius,
        param1=int(param1),
        param2=int(param2),
        minRadius=int(minRadius),  # Slightly smaller than expected radius
        maxRadius=int(minRadius)   # Slightly larger than expected radius
    )

    # If circles are detected, draw them on the output image
    if circles is not None:
        circles = np.uint16(np.around(circles))
        output_image = cv2.cvtColor(threshold_image, cv2.COLOR_GRAY2BGR)
        for (x, y, r) in circles[0, :]:
            cv2.circle(output_image, (x, y), r, (0, 255, 0), 2)
            cv2.circle(output_image, (x, y), 2, (0, 0, 255), 3)

        # Plot the output image
        plt.figure(figsize=(4, 4))
        plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
        plt.title('Detected Spheres')
        plt.axis('off')
        plt.show()

        return output_image, circles
    else:
        print("No circles were detected.")
        return None, None