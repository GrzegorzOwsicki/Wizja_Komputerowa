import cv2
import numpy as np

def update_mask(_):
    h_min = cv2.getTrackbarPos('H Min', 'Controls')
    s_min = cv2.getTrackbarPos('S Min', 'Controls')
    v_min = cv2.getTrackbarPos('V Min', 'Controls')
    h_max = cv2.getTrackbarPos('H Max', 'Controls')
    s_max = cv2.getTrackbarPos('S Max', 'Controls')
    v_max = cv2.getTrackbarPos('V Max', 'Controls')
    h2_min = cv2.getTrackbarPos('H Min2', 'Controls')
    s2_min = cv2.getTrackbarPos('S Min2', 'Controls')
    v2_min = cv2.getTrackbarPos('V Min2', 'Controls')
    h2_max = cv2.getTrackbarPos('H Max2', 'Controls')
    s2_max = cv2.getTrackbarPos('S Max2', 'Controls')
    v2_max = cv2.getTrackbarPos('V Max2', 'Controls')

    lower_skin = np.array([h_min, s_min, v_min], dtype=np.uint8)
    upper_skin = np.array([h_max, s_max, v_max], dtype=np.uint8)
    

    mask = cv2.inRange(hsv_image, lower_skin, upper_skin)

    lower_skin = np.array([h2_min, s2_min, v2_min], dtype=np.uint8)
    upper_skin = np.array([h2_max, s2_max, v2_max], dtype=np.uint8)

    mask2 = cv2.inRange(hsv_image, lower_skin, upper_skin)
    mask = mask+mask2
    skin_detected = cv2.bitwise_and(image, image, mask=mask)

    # Znajdowanie konturów
    gray = cv2.cvtColor(skin_detected, cv2.COLOR_BGR2GRAY)
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Rysowanie prostokątów wokół wykrytych obszarów
    result = image.copy()
    for contour in contours:
        if cv2.contourArea(contour) > 500:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.namedWindow('Detected Faces', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Detected Faces', 1280, 1024)
    cv2.imshow('Detected Faces', gray)

# Wczytaj obraz
image = cv2.imread('D:\wizja\wizja\wizjatest\image3.jpg')
#image = cv2.blur(image,(10,10))
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Tworzenie okna na suwaki
cv2.namedWindow('Controls', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Controls', 500, 300)

# Tworzenie suwaków dla zakresów HSV
cv2.createTrackbar('H Min', 'Controls', 0, 255, update_mask)
cv2.createTrackbar('S Min', 'Controls', 20, 255, update_mask)
cv2.createTrackbar('V Min', 'Controls', 150, 255, update_mask)
cv2.createTrackbar('H Max', 'Controls', 20, 255, update_mask)
cv2.createTrackbar('S Max', 'Controls', 200, 255, update_mask)
cv2.createTrackbar('V Max', 'Controls', 190, 255, update_mask)
cv2.createTrackbar('H Min2', 'Controls', 150, 255, update_mask)
cv2.createTrackbar('S Min2', 'Controls', 20, 255, update_mask)
cv2.createTrackbar('V Min2', 'Controls', 150, 255, update_mask)
cv2.createTrackbar('H Max2', 'Controls', 180, 255, update_mask)
cv2.createTrackbar('S Max2', 'Controls', 200, 255, update_mask)
cv2.createTrackbar('V Max2', 'Controls', 190, 255, update_mask)

# Pierwsza aktualizacja
update_mask(0)

# Główna pętla
cv2.waitKey(0)
cv2.destroyAllWindows()