import math
import tkinter as tk
from tkinter import filedialog, ttk, colorchooser
from detector import Detector

class GUI:
    def __init__(self, master):
        self.detector = Detector()
        self.display_stages = ["Obraz", "Progowanie adaptywne (maska1)", "Kolor skóry (maska2)", "maska1 AND maska2", "Wykryta skóra", "Odfiltrowane twarze"]

        self.master = master
        self.master.title("Parametry")

        # Create a menu bar
        menu_bar = tk.Menu(master)
        image_menu = tk.Menu(menu_bar, tearoff=0)
        image_menu.add_command(label="Otwórz", command=self.open_image)
        menu_bar.add_cascade(label="Obraz", menu=image_menu)
        param_menu = tk.Menu(menu_bar, tearoff=0)
        param_menu.add_command(label="Wczytaj", command=self.load_params)
        param_menu.add_command(label="Zapisz", command=self.save_params)
        menu_bar.add_cascade(label="Parametry", menu=param_menu)
        master.config(menu=menu_bar)

        # Create a tab control
        self.tab_control = ttk.Notebook(master)

        # Uwydatnianie obrazu
        self.image_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.image_tab, text='Uwydatnianie obrazu')

        self.white_balance_var = tk.BooleanVar(value=False)

        self.hist_h_var = tk.BooleanVar(value=False)
        self.hist_s_var = tk.BooleanVar(value=False)
        self.hist_v_var = tk.BooleanVar(value=False)

        self.gamma = tk.Scale(self.image_tab, from_=0, to=5, resolution=0.01, orient='horizontal', command=self.update_params, label="Gamma")
        self.gamma.pack(fill='x')

        self.white_balance_check =tk.Checkbutton(self.image_tab, text="Balans bieli", command=self.update_params, variable=self.white_balance_var)
        self.white_balance_check.pack(anchor='w')

        self.hist_label = tk.Label(self.image_tab, text="Wyrównaj histogram").pack(anchor='w')
        self.hist_h_check =tk.Checkbutton(self.image_tab, text="Hue", command=self.update_params, variable=self.hist_h_var)
        self.hist_h_check.pack(anchor='w')
        self.hist_s_check =tk.Checkbutton(self.image_tab, text="Saturation", command=self.update_params, variable=self.hist_s_var)
        self.hist_s_check.pack(anchor='w')
        self.hist_v_check =tk.Checkbutton(self.image_tab, text="Value", command=self.update_params, variable=self.hist_v_var)
        self.hist_v_check.pack(anchor='w')

        self.blur_gauss_size = tk.Scale(self.image_tab, from_=1, to=31, orient='horizontal', command=self.update_params, label="Rozmycie Gaussa (rozmiar, sigma)")
        self.blur_gauss_sigma = tk.Scale(self.image_tab, from_=0, to=32, resolution=0.01, orient='horizontal', command=self.update_params)
        self.blur_gauss_size.pack(fill='x')
        self.blur_gauss_sigma.pack(fill='x')

        self.blur_median_size = tk.Scale(self.image_tab, from_=1, to=31, orient='horizontal', command=self.update_params, label="Rozmycie medianowe (rozmiar)")  
        self.blur_median_size.pack(fill='x')

        # Progowanie adaptywne
        self.adaptiveThreshold_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.adaptiveThreshold_tab, text='Progowanie adaptywne')

        self.adaptive_threshold_h = tk.BooleanVar(value=False)
        self.adaptive_threshold_s = tk.BooleanVar(value=False)
        self.adaptive_threshold_v = tk.BooleanVar(value=False)

        self.adaptive_threshold_size = tk.Scale(self.adaptiveThreshold_tab, from_=3, to=63, orient='horizontal', command=self.update_params, label="Progowanie Adaptywne (rozmiar, stała C)")
        self.adaptive_threshold_size.pack(fill='x')
        self.adaptive_threshold_c = tk.Scale(self.adaptiveThreshold_tab, from_=-32, to=32, orient='horizontal', command=self.update_params)
        self.adaptive_threshold_c.pack(fill='x')

        self.adaptive_threshold_h_check =tk.Checkbutton(self.adaptiveThreshold_tab, text="Hue", command=self.update_params, variable=self.adaptive_threshold_h)
        self.adaptive_threshold_h_check.pack(anchor='w')
        self.adaptive_threshold_s_check =tk.Checkbutton(self.adaptiveThreshold_tab, text="Saturation", command=self.update_params, variable=self.adaptive_threshold_s)
        self.adaptive_threshold_s_check.pack(anchor='w')
        self.adaptive_threshold_v_check =tk.Checkbutton(self.adaptiveThreshold_tab, text="Value", command=self.update_params, variable=self.adaptive_threshold_v)
        self.adaptive_threshold_v_check.pack(anchor='w')

        self.adaptive_threshold_erode_dilate_size = tk.Scale(self.adaptiveThreshold_tab, from_=3, to=31, orient='horizontal', command=self.update_params, label="Erozja - Dylatacja (rozmiar - iteracje)")
        self.adaptive_threshold_erode_dilate_iter = tk.Scale(self.adaptiveThreshold_tab, from_=-16, to=16, orient='horizontal', command=self.update_params)
        self.adaptive_threshold_erode_dilate_size.pack(fill='x')
        self.adaptive_threshold_erode_dilate_iter.pack(fill='x')

        # Kolor skóry
        self.skin_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.skin_tab, text='Kolor skóry')

        self.hue_min = tk.Scale(self.skin_tab, from_=0, to=179, orient='horizontal', command=self.update_params, label="Hue (min - max)")
        self.hue_max = tk.Scale(self.skin_tab, from_=0, to=179, orient='horizontal', command=self.update_params)
        self.hue_min.pack(fill='x')
        self.hue_max.pack(fill='x')

        self.saturation_min = tk.Scale(self.skin_tab, from_=0, to=255, orient='horizontal', command=self.update_params, label="Saturation (min - max)")
        self.saturation_max = tk.Scale(self.skin_tab, from_=0, to=255, orient='horizontal', command=self.update_params)
        self.saturation_min.pack(fill='x')
        self.saturation_max.pack(fill='x')

        self.value_min = tk.Scale(self.skin_tab, from_=0, to=255, orient='horizontal', command=self.update_params, label="Value (min - max)")
        self.value_max = tk.Scale(self.skin_tab, from_=0, to=255, orient='horizontal', command=self.update_params)
        self.value_min.pack(fill='x')
        self.value_max.pack(fill='x')

        self.erode_dilate_size = tk.Scale(self.skin_tab, from_=3, to=31, orient='horizontal', command=self.update_params, label="Erozja - Dylatacja (rozmiar - iteracje)")
        self.erode_dilate_iter = tk.Scale(self.skin_tab, from_=-16, to=16, orient='horizontal', command=self.update_params)
        self.erode_dilate_size.pack(fill='x')
        self.erode_dilate_iter.pack(fill='x')

        # Filtrowanie
        self.filter_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.filter_tab, text='Filtrowanie')

        self.area_min = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal',command=self.update_params, label="Pole KONTURU (min - max)")
        self.area_min.pack(fill='x')
        self.area_max = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal',command=self.update_params)
        self.area_max.pack(fill='x')

        self.aspect_ratio_min = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal', command=self.update_params, label="Proporcje (min - max) 1 = kwadrat")
        self.aspect_ratio_max = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal', command=self.update_params)
        self.aspect_ratio_min.pack(fill='x')
        self.aspect_ratio_max.pack(fill='x')

        self.circularity_min = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal', command=self.update_params, label="Okrągłość (min - max)")
        self.circularity_min.pack(fill='x')
        self.circularity_max = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal', command=self.update_params)
        self.circularity_max.pack(fill='x')

        # Wyświetlanie
        self.display_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.display_tab, text='Wyświetlanie')

        self.display_stage = tk.Scale(self.display_tab, label="Faza przetwarzania", from_=0, to=5, orient='horizontal', command=self.update_params)
        self.display_stage.pack(fill='x')

        self.contour_var = tk.BooleanVar(value=False)
        self.rectangle_var = tk.BooleanVar(value=False)
        self.ellipse_var = tk.BooleanVar(value=False)
        self.mask_enhanced_var = tk.BooleanVar(value=False)

        self.contour_check = tk.Checkbutton(self.display_tab, text="Kontury", command=self.update_params, variable=self.contour_var)
        self.contour_check.pack(anchor='w', pady=(5,0))
        self.rectangle_check =tk.Checkbutton(self.display_tab, text="Prostokąty", command=self.update_params, variable=self.rectangle_var)
        self.rectangle_check.pack(anchor='w')
        self.ellipse_check = tk.Checkbutton(self.display_tab, text="Elipsy", command=self.update_params, variable=self.ellipse_var)
        self.ellipse_check.pack(anchor='w')
        self.mask_enhanced_check = tk.Checkbutton(self.display_tab, text="Obraz uwydatniony", command=self.update_params, variable=self.mask_enhanced_var)
        self.mask_enhanced_check.pack(anchor='w', pady=(5,0))

        # Pack the tab control
        self.tab_control.pack(expand=1, fill='both')
        self.tab_control.select(self.skin_tab)
        
        self.init_params()

    def init_params(self):
        p = self.detector.params

        self.gamma.set(p.gamma)
        self.white_balance_var.set(p.white_balance)
        self.hist_h_var.set(p.hist_h)
        self.hist_s_var.set(p.hist_s)
        self.hist_v_var.set(p.hist_v)
        self.blur_gauss_size.set(p.blur_gauss_size)
        self.blur_gauss_sigma.set(p.blur_gauss_sigma)
        self.blur_median_size.set(p.blur_median_size)

        self.adaptive_threshold_h.set(p.adaptive_threshold_h)
        self.adaptive_threshold_s.set(p.adaptive_threshold_s)
        self.adaptive_threshold_v.set(p.adaptive_threshold_v)
        self.adaptive_threshold_size.set(p.adaptive_threshold_size)
        self.adaptive_threshold_c.set(p.adaptive_threshold_c)
        self.adaptive_threshold_erode_dilate_size.set(p.adaptive_threshold_erode_dilate_size)
        self.adaptive_threshold_erode_dilate_iter.set(p.adaptive_threshold_erode_dilate_iter)

        self.hue_min.set(p.hue_min)
        self.hue_max.set(p.hue_max)
        self.saturation_min.set(p.saturation_min)
        self.saturation_max.set(p.saturation_max)
        self.value_min.set(p.value_min)
        self.value_max.set(p.value_max)
        self.erode_dilate_size.set(p.erode_dilate_size)
        self.erode_dilate_iter.set(p.erode_dilate_iter)

        self.area_min.set(p.area_min)
        self.area_max.set(p.area_max)
        self.aspect_ratio_min.set(p.aspect_ratio_min)
        self.aspect_ratio_max.set(p.aspect_ratio_max)
        self.circularity_min.set(p.circularity_min)
        self.circularity_max.set(p.circularity_max)

        pd = self.detector.display
        self.display_stage.config(label="Faza przetwarzania:    "+self.display_stages[pd.stage])
        self.display_stage.set(pd.stage)
        self.contour_var.set(pd.contours)
        self.rectangle_var.set(pd.rectangles)
        self.ellipse_var.set(pd.ellipses)
        self.mask_enhanced_var.set(pd.mask_enhanced)

    def update_params(self, event=None):
        self.detector.params.gamma = self.gamma.get()
        self.detector.params.white_balance = self.white_balance_var.get()
        self.detector.params.hist_h = self.hist_h_var.get()
        self.detector.params.hist_s = self.hist_s_var.get()
        self.detector.params.hist_v = self.hist_v_var.get()
        if self.blur_gauss_size.get() % 2 == 0:
            self.blur_gauss_size.set(self.blur_gauss_size.get()+1)
        self.detector.params.blur_gauss_size = self.blur_gauss_size.get()
        self.detector.params.blur_gauss_sigma = self.blur_gauss_sigma.get()
        if self.blur_median_size.get() % 2 == 0:
            self.blur_median_size.set(self.blur_median_size.get()+1)
        self.detector.params.blur_median_size = self.blur_median_size.get()

        self.detector.params.adaptive_threshold_h = self.adaptive_threshold_h.get()
        self.detector.params.adaptive_threshold_s = self.adaptive_threshold_s.get()
        self.detector.params.adaptive_threshold_v = self.adaptive_threshold_v.get()
        if self.adaptive_threshold_size.get() % 2 == 0:
            self.adaptive_threshold_size.set(self.adaptive_threshold_size.get()+1)
        self.detector.params.adaptive_threshold_size = self.adaptive_threshold_size.get()
        self.detector.params.adaptive_threshold_c = self.adaptive_threshold_c.get()
        if self.adaptive_threshold_erode_dilate_size.get() % 2 == 0:
            self.adaptive_threshold_erode_dilate_size.set(self.adaptive_threshold_erode_dilate_size.get()+1)
        self.detector.params.adaptive_threshold_erode_dilate_size = self.adaptive_threshold_erode_dilate_size.get()
        self.detector.params.adaptive_threshold_erode_dilate_iter = self.adaptive_threshold_erode_dilate_iter.get()

        self.detector.params.hue_min = self.hue_min.get()
        self.detector.params.hue_max = self.hue_max.get()
        self.detector.params.saturation_min = self.saturation_min.get()
        self.detector.params.saturation_max = self.saturation_max.get()
        self.detector.params.value_min = self.value_min.get()
        self.detector.params.value_max = self.value_max.get()
        if self.erode_dilate_size.get() % 2 == 0:
            self.erode_dilate_size.set(self.erode_dilate_size.get()+1)
        self.detector.params.erode_dilate_size = self.erode_dilate_size.get()
        self.detector.params.erode_dilate_iter = self.erode_dilate_iter.get()

        self.detector.params.area_min = self.area_min.get()
        self.detector.params.area_max = self.area_max.get()
        self.detector.params.aspect_ratio_min = self.aspect_ratio_min.get()
        self.detector.params.aspect_ratio_max = self.aspect_ratio_max.get()
        self.detector.params.circularity_min = self.circularity_min.get()
        self.detector.params.circularity_max = self.circularity_max.get()

        self.detector.display.stage = self.display_stage.get()
        self.display_stage.config(label="Faza przetwarzania:    "+self.display_stages[self.display_stage.get()])
        self.detector.display.contours = self.contour_var.get()
        self.detector.display.rectangles = self.rectangle_var.get()
        self.detector.display.ellipses = self.ellipse_var.get()
        self.detector.display.mask_enhanced = self.mask_enhanced_var.get()
        
        self.detector.update()

    def open_image(self):
        file_path = filedialog.askopenfilename(
            initialdir=".",
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.webp")]
            
        )
        if file_path:
            self.detector.openImage(file_path)
            self.detector.update()

    def save_params(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="parameters.json",
            initialdir=".",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.detector.saveParameters(file_path)

    def load_params(self):
        file_path = filedialog.askopenfilename(
            initialdir=".",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.detector.loadParameters(file_path)
            self.init_params()
            self.detector.update()
