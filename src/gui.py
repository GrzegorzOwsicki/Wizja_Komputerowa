import tkinter as tk
from tkinter import filedialog, ttk, colorchooser
from detector import Detector

class GUI:
    def __init__(self, master):
        self.detector = Detector()

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

        # Filtrowanie
        self.filter_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.filter_tab, text='Filtrowanie')

        self.area_min = tk.Scale(self.filter_tab, from_=0, to=2000, orient='horizontal', command=self.update_params, label="Pole (min)")
        self.area_min.pack(fill='x')

        self.aspect_ratio_min = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal', command=self.update_params, label="Proporcje (min - max) 1 = kwadrat")
        self.aspect_ratio_max = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal', command=self.update_params)
        self.aspect_ratio_min.pack(fill='x')
        self.aspect_ratio_max.pack(fill='x')

        self.circularity_min = tk.Scale(self.filter_tab, from_=0, to=1, resolution=0.01, orient='horizontal', command=self.update_params, label="Okrągłość (min)")
        self.circularity_min.pack(fill='x')

        # Wyświetlanie
        self.display_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.display_tab, text='Wyświetlanie')

        self.display_stage = tk.Scale(self.display_tab, from_=0, to=5, orient='horizontal', command=self.update_params)
        self.display_stage.pack(fill='x')

        self.contour_var = tk.BooleanVar(value=False)
        self.rectangle_var = tk.BooleanVar(value=False)
        self.ellipse_var = tk.BooleanVar(value=False)

        self.contour_check = tk.Checkbutton(self.display_tab, text="Kontury", command=self.update_params, variable=self.contour_var)
        self.contour_check.pack(anchor='w')
        self.rectangle_check =tk.Checkbutton(self.display_tab, text="Prostokąty", command=self.update_params, variable=self.rectangle_var)
        self.rectangle_check.pack(anchor='w')
        self.ellipse_check = tk.Checkbutton(self.display_tab, text="Elipsy", command=self.update_params, variable=self.ellipse_var)
        self.ellipse_check.pack(anchor='w')

        # Pack the tab control
        self.tab_control.pack(expand=1, fill='both')
        self.tab_control.select(self.skin_tab)
        
        self.init_params()

    def init_params(self):
        p = self.detector.params
        self.hue_min.set(p.hue_min)
        self.hue_max.set(p.hue_max)
        self.saturation_min.set(p.saturation_min)
        self.saturation_max.set(p.saturation_max)
        self.value_min.set(p.value_min)
        self.value_max.set(p.value_max)

        self.area_min.set(p.area_min)
        self.aspect_ratio_min.set(p.aspect_ratio_min)
        self.aspect_ratio_max.set(p.aspect_ratio_max)
        self.circularity_min.set(p.circularity_min)

        pd = self.detector.display
        self.display_stage.set(pd.stage)
        self.contour_var.set(pd.contours)
        self.rectangle_var.set(pd.rectangles)
        self.ellipse_var.set(pd.ellipses)

    def update_params(self, event=None):
        self.detector.params.hue_min = self.hue_min.get()
        self.detector.params.hue_max = self.hue_max.get()
        self.detector.params.saturation_min = self.saturation_min.get()
        self.detector.params.saturation_max = self.saturation_max.get()
        self.detector.params.value_min = self.value_min.get()
        self.detector.params.value_max = self.value_max.get()

        self.detector.params.area_min = self.area_min.get()
        self.detector.params.aspect_ratio_min = self.aspect_ratio_min.get()
        self.detector.params.aspect_ratio_max = self.aspect_ratio_max.get()
        self.detector.params.circularity_min = self.circularity_min.get()

        self.detector.display.stage = self.display_stage.get()
        self.detector.display.contours = self.contour_var.get()
        self.detector.display.rectangles = self.rectangle_var.get()
        self.detector.display.ellipses = self.ellipse_var.get()
        
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
