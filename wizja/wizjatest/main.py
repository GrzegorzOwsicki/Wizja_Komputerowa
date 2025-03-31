import cv2
import numpy as np

# Load the image
image = cv2.imread('D:\wizja\wizja\wizjatest\image3.jpg')
image = cv2.blur(image,(6,6))
# Convert the image to HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the range for skin color in HSV
lower_skin = np.array([0, 20, 130], dtype=np.uint8)
upper_skin = np.array([20, 255, 255], dtype=np.uint8)

# Create a mask using the skin color range
mask = cv2.inRange(hsv_image, lower_skin, upper_skin)

lower_skin = np.array([170, 0, 0], dtype=np.uint8)
upper_skin = np.array([180, 255, 255], dtype=np.uint8)

# Create a mask using the skin color range
mask2 = cv2.inRange(hsv_image, lower_skin, upper_skin)

mask = mask+mask2

# Apply the mask to the image
skin_detected = cv2.bitwise_and(image, image, mask=mask)

# Convert the result to grayscale
gray = cv2.cvtColor(skin_detected, cv2.COLOR_BGR2GRAY)

# Find contours in the mask
contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw bounding boxes around detected faces (contours)
for contour in contours:
    if cv2.contourArea(contour) > 500:  # Filter out small areas
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)



window_width = 1024
window_height = 1280
cv2.namedWindow('Detected Faces', cv2.WINDOW_NORMAL)  # Allow window resizing
cv2.resizeWindow('Detected Faces', window_width, window_height)
# Display the result
cv2.imshow('Detected Faces', image)
cv2.waitKey(0)
cv2.destroyAllWindows()


