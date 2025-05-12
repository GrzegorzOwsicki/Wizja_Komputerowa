import cv2
import numpy as np
import json

class Parameters:
    def __init__(self):
        # Uwydatnianie obrazu
        self.gamma = 1
        self.white_balance = False
        self.hist_h = False
        self.hist_s = False
        self.hist_v = False
        self.blur_gauss_size = 1
        self.blur_gauss_sigma = 0.5
        self.blur_median_size = 1

        # Progowanie adaptywne
        self.adaptive_threshold_h = False
        self.adaptive_threshold_s = False
        self.adaptive_threshold_v = False
        self.adaptive_threshold_size = 21
        self.adaptive_threshold_c = 6
        self.adaptive_threshold_erode_dilate_size = 3
        self.adaptive_threshold_erode_dilate_iter = 0

        # Kolor skóry
        self.hue_min = 0
        self.hue_max = 15
        self.saturation_min = 20
        self.saturation_max = 255
        self.value_min = 0
        self.value_max = 255
        self.erode_dilate_size = 3
        self.erode_dilate_iter = 0
        self.YCrBr_lower = (0, 133, 77)
        self.YCrBr_upper = (255, 173, 127)

        # Filtracja wyników
        self.area_min = 0.1
        self.area_max = 0.5
        self.aspect_ratio_min = 0.4
        self.aspect_ratio_max = 1
        self.circularity_min = 0.5
        self.circularity_max = 1

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
        self.mask_enhanced = True

class Detector:
    def __init__(self):
        self.image = None
        self.imageWidth = 0 # nie używane
        self.imageHeight = 0 # nie używane
        self.imageArea = 0 # używane w filterArea
        self.params = Parameters()
        self.display = DisplayParams()

    def openImage(self, filename):
        self.image = cv2.imread(filename)
        height, width, channels = self.image.shape
        self.imageArea = width * height
        self.imageWidth = width
        self.imageHeight = height

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
        image_gamma_corrected = self.imageGamma(self.image)
        image_balanced = self.imageWhiteBalance(image_gamma_corrected)
        image_equalized = self.imageEqualize(image_balanced)
        image_blur_gauss = self.imageBlurGauss(image_equalized)
        image_blur_median = self.imageBlurMedian(image_blur_gauss)

        image_enhanced = image_blur_median
        image_hsv = cv2.cvtColor(image_enhanced, cv2.COLOR_BGR2HSV)
        image_YCrBr = cv2.cvtColor(image_enhanced,cv2.COLOR_BGR2YCR_CB)

        # Maskowanie
        mask_adaptiveThreshold = self.maskAdaptiveThreshold(image_hsv)
        mask_skinColor = self.maskSkinColor(image_hsv,image_YCrBr)
        mask = cv2.bitwise_and(mask_skinColor, mask_adaptiveThreshold)
     
        display_image = image_enhanced if self.display.mask_enhanced else self.image
        skin = cv2.bitwise_and(display_image, display_image, mask=mask)

        # Detekcja konturów
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = list(contours)

        def get_contours_mask_skin(contours):
            newMask = np.zeros_like(mask, dtype=np.uint8)
            cv2.drawContours(newMask, contours, -1, 255, thickness=cv2.FILLED)
            newSkin = cv2.bitwise_and(display_image, display_image, mask=newMask)
            return newMask, newSkin

        # Filtracja Wyników
        contours = list(filter(self.filterCanFitElipse, contours))
        contours = list(filter(self.filterArea, contours))
        maskFilterArea, skinFilterArea = get_contours_mask_skin(contours)
        contours = list(filter(self.filterAspectRatio, contours))
        maskFilterAspectRatio, skinFilterAspectRatio = get_contours_mask_skin(contours)
        contours = [cnt for cnt in contours if self.filterCircularity(cnt, mask)] # To samo tylko zapisane inaczej aby dodać dodatkowy parametr mask
        maskFilterCircularity, skinFilterCircularity = get_contours_mask_skin(contours)
        
        skinFiltered = skinFilterCircularity

        # Wyświetlanie wyniku
        self.displayResult(contours, 
            [
                display_image,
                mask_adaptiveThreshold,
                mask_skinColor, 
                mask,
                skin, 
                skinFiltered
            ])

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

    def maskAdaptiveThreshold(self, image_hsv):
        p = self.params
        image_h, image_s, image_v = cv2.split(image_hsv)
        mask_h = np.ones_like(image_h, dtype=np.uint8) * 255
        mask_s = mask_h.copy()
        mask_v = mask_h.copy()
        if p.adaptive_threshold_h:
            mask_h = cv2.adaptiveThreshold(image_h, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, p.adaptive_threshold_size, p.adaptive_threshold_c)
        if p.adaptive_threshold_s:
            mask_s = cv2.adaptiveThreshold(image_s, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, p.adaptive_threshold_size, p.adaptive_threshold_c)
        if p.adaptive_threshold_v:
            mask_v = cv2.adaptiveThreshold(image_v, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, p.adaptive_threshold_size, p.adaptive_threshold_c)
        mask = cv2.bitwise_and(mask_h, mask_s, mask=mask_v)

        # Erozja - Dylatacja
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (p.adaptive_threshold_erode_dilate_size, p.adaptive_threshold_erode_dilate_size))
        maskErodeDilate = mask.copy()
        if p.adaptive_threshold_erode_dilate_iter < 0: # Erode
            maskErodeDilate = cv2.erode(maskErodeDilate, kernel, iterations=p.adaptive_threshold_erode_dilate_iter*-1)
        elif p.adaptive_threshold_erode_dilate_iter > 0: # Dilate
            maskErodeDilate = cv2.dilate(maskErodeDilate, kernel, iterations=p.adaptive_threshold_erode_dilate_iter)

        return maskErodeDilate
        

    def maskSkinColor(self, image_hsv, image_YCrBr):
        p = self.params
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
        
        
        # porównanie z maaską YCrBr
        mask2 = cv2.inRange(image_YCrBr,p.YCrBr_lower,p.YCrBr_upper)
        mask = cv2.bitwise_and(mask,mask2)

        # Erozja - Dylatacja
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (p.erode_dilate_size, p.erode_dilate_size))
        maskErodeDilate = mask.copy()
        if p.erode_dilate_iter < 0: # Erode
            maskErodeDilate = cv2.erode(maskErodeDilate, kernel, iterations=p.erode_dilate_iter*-1)
        elif p.erode_dilate_iter > 0: # Dilate
            maskErodeDilate = cv2.dilate(maskErodeDilate, kernel, iterations=p.erode_dilate_iter)

        return maskErodeDilate

    def imageWhiteBalance(self, image):
        """
        Perform white balance using Gray World Assumption.
        """
        p = self.params
        if p.white_balance == False:
            return image
        result = image.copy().astype(np.float32)

        avg_b = np.mean(result[:, :, 0])
        avg_g = np.mean(result[:, :, 1])
        avg_r = np.mean(result[:, :, 2])

        avg_gray = (avg_b + avg_g + avg_r) / 3

        # Scale each channel so that the avg becomes avg_gray
        result[:, :, 0] *= (avg_gray / avg_b)
        result[:, :, 1] *= (avg_gray / avg_g)
        result[:, :, 2] *= (avg_gray / avg_r)

        # Clip to [0, 255] and convert back
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result

    def imageEqualize(self, image):
        p = self.params
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(image_hsv)
        h_eq = cv2.equalizeHist(h) if p.hist_h else h
        s_eq = cv2.equalizeHist(s) if p.hist_s else s
        v_eq = cv2.equalizeHist(v) if p.hist_v else v
        image_hsv = cv2.merge((h_eq, s_eq, v_eq))
        image_bgr = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)
        return image_bgr

    def imageGamma(self, image):
        normalized_image = image / 255.0
        corrected_image = np.power(normalized_image, self.params.gamma)
        corrected_image = np.uint8(corrected_image * 255)
        return corrected_image

    def imageBlurGauss(self, image):
        p = self.params
        if p.blur_gauss_size < 2:
            return image
        if p.blur_gauss_size % 2 == 0:
            p.blur_gauss_size += 1
        return cv2.GaussianBlur(image, (p.blur_gauss_size, p.blur_gauss_size), p.blur_gauss_sigma)
    
    def imageBlurMedian(self, image):
        p = self.params
        if p.blur_median_size < 2:
            return image
        if p.blur_median_size % 2 == 0:
            p.blur_median_size += 1
        return cv2.medianBlur(image, p.blur_median_size)

    def filterCanFitElipse(self, contour):
        return len(contour) >= 5 # cv2.fitEllipse wymaga minimum 5 punktów w konturze

    def filterArea(self, contour):
        # POLE KONTURU A NIE KWADRATU
        area = cv2.contourArea(contour)
        areaPct = area / self.imageArea

        # Zauważyłem że pola często są w bardzo małych wartościach typu 0.05
        # Dlatego aby uprościć parametr w gui, zostaje tutaj zmieniona jego skala
        # Jako skutek uboczny parametr już nie odzwierciedla % powierzchni
        # Tutaj robimy skalę pierwiastek o podstawie 2, polecam sobie zobaczyć na wykresie jak to wygląda
        # https://www.desmos.com/calculator/r0hnoridtu
        areaPct = areaPct ** 0.5 

        return self.params.area_min <= areaPct <= self.params.area_max

    def filterAspectRatio(self, contour):
        # Obliczamy proporcje za pomocą elips bo uwzględniane są pod każdym kątem obrotu
        ellipse = cv2.fitEllipse(contour)
        major_axis, minor_axis = ellipse[1] 
        if minor_axis == 0:
            return False
    
        aspect_ratio = major_axis / minor_axis
        
        p = self.params
        if (p.aspect_ratio_min > p.aspect_ratio_max):
            return aspect_ratio <= p.aspect_ratio_max or aspect_ratio >= p.aspect_ratio_min

        return p.aspect_ratio_min <= aspect_ratio <= p.aspect_ratio_max

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

        # Część wspólna i różna
        total = cv2.bitwise_or(contour_region, ellipse_mask)
        total_pixels = cv2.countNonZero(total)

        if total_pixels == 0:
            return False

        circularity = overlap_pixels / total_pixels
        return self.params.circularity_min <= circularity <= self.params.circularity_max 
