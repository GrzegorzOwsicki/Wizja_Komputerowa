import cv2
import numpy as np
import json

class Parameters:
    def __init__(self):
        # Uwydatnianie obrazu

        # Kolor skóry
        self.hue_min = 0
        self.hue_max = 15
        self.saturation_min = 20
        self.saturation_max = 255
        self.value_min = 0
        self.value_max = 255

        # Filtracja wyników
        self.area_min = 300
        self.aspect_ratio_min = 0.5
        self.aspect_ratio_max = 2
        self.circularity_min = 0.75

class DisplayParams:
    def __init__(self):
        self.display = True
        self.stage = 0
        self.contours = False
        self.contour_color = (0,0,255)
        self.contour_thick = 3
        self.rectangles = True
        self.rectangle_color = (0,255,0)
        self.rectangle_thick = 3
        self.ellipses = False
        self.ellipse_color = (255,0,0)
        self.ellipse_thick = 3

class Detector:
    def __init__(self):
        self.image = None
        self.params = Parameters()
        self.display = DisplayParams()

    def openImage(self, filename):
        self.image = cv2.imread(filename)

    def saveParameters(self, filepath):
        with open(filepath, 'w') as file:
            json.dump(self.params.__dict__, file, indent=4)

    def loadParameters(self, filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
            self.params.__dict__.update(data)

    def update(self):
        if self.image is None: return []
        p = self.params

        # Uwydatnianie obrazu
        image_hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        # Maskowanie koloru skóry
        def get_ranges(min_val, max_val, max_range):
            if min_val <= max_val:
                # Przedział wewnętrzny
                return [(min_val, max_val)]
            else:
                # Jeżeli minimum i maksimum są na odwrót
                # Brane są przedziały zewnętrzne
                return [(0, max_val), (min_val, max_range)]

        hue_ranges = get_ranges(p.hue_min, p.hue_max, 179)
        sat_ranges = get_ranges(p.saturation_min, p.saturation_max, 255)
        val_ranges = get_ranges(p.value_min, p.value_max, 255)

        mask = None # Złożenie maski ze wszyskich przedziałów
        for h_min, h_max in hue_ranges:
            for s_min, s_max in sat_ranges:
                for v_min, v_max in val_ranges:
                    lower = (h_min, s_min, v_min)
                    upper = (h_max, s_max, v_max)
                    temp_mask = cv2.inRange(image_hsv, lower, upper)
                    if mask is None:
                        mask = temp_mask
                    else:
                        mask = cv2.bitwise_or(mask, temp_mask)
        skin = cv2.bitwise_and(self.image, self.image, mask=mask)

        # Detekcja konturów
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = list(contours)

        def get_contours_mask_skin(contours):
            newMask = np.zeros_like(mask, dtype=np.uint8)
            cv2.drawContours(newMask, contours, -1, 255, thickness=cv2.FILLED)
            newSkin = cv2.bitwise_and(self.image, self.image, mask=newMask)
            return newMask, newSkin

        # Filtracja Wyników
        contours = list(filter(self.filterCanFitElipse, contours))
        contours = list(filter(self.filterArea, contours))
        mask1, skin1 = get_contours_mask_skin(contours)
        contours = list(filter(self.filterAspectRatio, contours))
        mask2, skin2 = get_contours_mask_skin(contours)
        contours = [cnt for cnt in contours if self.filterCircularity(cnt, mask)] # To samo tylko zapisane inaczej aby dodać dodatkowy parametr mask
        mask3, skin3 = get_contours_mask_skin(contours)

        # Wyświetlanie wyniku
        self.displayResult(contours, [self.image, mask, skin, skin1, skin2, skin3])

        return contours

    def displayResult(self, contours, stages):
        dp = self.display
        if not self.display:
            return
        display = stages[dp.stage].copy()

        try: # Zamiana obrazów w skali szarości na kolorowe aby wyświetlać kolorowe oznaczenia
            display = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
        except:
            None

        if (dp.contours):
            cv2.drawContours(display, contours, -1, dp.contour_color, dp.contour_thick)
        for contour in contours:
            if (dp.rectangles):
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(display, (x, y), (x + w, y + h), dp.rectangle_color, dp.rectangle_thick)
            if (dp.ellipses):
                ellipse = cv2.fitEllipse(contour)
                cv2.ellipse(display, ellipse, dp.ellipse_color, dp.ellipse_thick)
        
        cv2.namedWindow("Detekcja Twarzy", cv2.WINDOW_KEEPRATIO)
        cv2.imshow("Detekcja Twarzy", display)

    def filterCanFitElipse(self, contour):
        return len(contour) >= 5 # cv2.fitEllipse wymaga minimum 5 punktów w konturze

    def filterArea(self, contour):
        return cv2.contourArea(contour) > self.params.area_min

    def filterAspectRatio(self, contour):
        # Obliczamy proporcje za pomocą elips bo uwzględniane są pod każdym kątem obrotu
        ellipse = cv2.fitEllipse(contour)
        major_axis, minor_axis = ellipse[1] 
        if minor_axis == 0:
            return False
    
        aspect_ratio = major_axis / minor_axis
        
        p = self.params
        if (p.aspect_ratio_min > p.aspect_ratio_max):
            return aspect_ratio < p.aspect_ratio_max or aspect_ratio > p.aspect_ratio_min

        return p.aspect_ratio_min < aspect_ratio < p.aspect_ratio_max

    def filterCircularity(self, contour, mask):
        ellipse = cv2.fitEllipse(contour)

        # Pole konturu
        contour_region = np.zeros_like(mask, dtype=np.uint8)
        cv2.drawContours(contour_region, [contour], -1, 255, thickness=cv2.FILLED)

        # Pole elipsy
        ellipse_mask = np.zeros_like(mask, dtype=np.uint8)
        cv2.ellipse(ellipse_mask, ellipse, 255, thickness=cv2.FILLED)

        # Część wspólna
        overlap = cv2.bitwise_and(contour_region, ellipse_mask)
        overlap_pixels = cv2.countNonZero(overlap)

        # Część elipsy poza konturem
        spill1 = cv2.bitwise_and(cv2.bitwise_not(contour_region), ellipse_mask)
        spill1_pixels = cv2.countNonZero(spill1)

        # Część konturu poza elipsą
        spill2 = cv2.bitwise_and(contour_region, cv2.bitwise_not(ellipse_mask))
        spill2_pixels = cv2.countNonZero(spill2)

        total_evaluated = overlap_pixels + spill1_pixels + spill2_pixels
        if total_evaluated == 0:
            return False

        circularity = overlap_pixels / total_evaluated
        return circularity >= self.params.circularity_min
