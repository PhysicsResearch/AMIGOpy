import numpy as np
import matplotlib.pyplot as plt
import cv2

def plot_image(image, title):
    plt.figure(figsize=(4, 4))
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.axis('off')

def detect_low_intensity_spheres(image, expected_diameter=14):
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
    _, threshold_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Plot the thresholded image
    plot_image(threshold_image, 'Thresholded Image')

    # Detect circles using the Hough Circle Transform
    circles = cv2.HoughCircles(
        threshold_image,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=expected_diameter,
        param1=50,
        param2=30,
        minRadius=expected_diameter//2 - 7,  # Slightly smaller than expected radius
        maxRadius=expected_diameter//2 + 7   # Slightly larger than expected radius
    )

    # If circles are detected, draw them on the output image
    if circles is not None:
        circles = np.uint16(np.around(circles))
        output_image = cv2.cvtColor(normalized_image, cv2.COLOR_GRAY2BGR)
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