import cv2
import tkinter as tk
from gui import GUI

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()