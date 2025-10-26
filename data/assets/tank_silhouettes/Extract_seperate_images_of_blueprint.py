import cv2
import numpy as np
import os
from tkinter import Tk, filedialog, Button, Label, Frame, Canvas, Scrollbar, Toplevel
from PIL import Image, ImageTk

# === CONFIG ===
OUTPUT_FOLDER = "cropped_views"
MIN_CONTOUR_AREA = 1000  # filter out noise

# === ADAPTIVE MASKING ===
def create_alpha_mask(cropped):
    if cropped.shape[2] == 4:
        return cropped[:, :, 3]
    else:
        gray = cv2.cvtColor(cropped[:, :, :3], cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        return mask

# === QUADRANT ASSIGNMENT ===
def assign_quadrant(cx, cy, width, height):
    if cx < width / 2 and cy < height / 2:
        return "front"
    elif cx >= width / 2 and cy < height / 2:
        return "side"
    elif cx < width / 2 and cy >= height / 2:
        return "rear"
    else:
        return "top"

# === SEMANTIC VIEW DETECTION ===
def detect_semantic_views(img, filename):
    height, width = img.shape[:2]
    alpha = create_alpha_mask(img)
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_CONTOUR_AREA]

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    previews = []

    preview_window = Toplevel()
    preview_window.title("Preview Semantic Views")
    canvas = Canvas(preview_window)
    scrollbar = Scrollbar(preview_window, orient="vertical", command=canvas.yview)
    scroll_frame = Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    quadrant_map = {}

    for cnt in filtered:
        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2
        label = assign_quadrant(cx, cy, width, height)

        # Avoid duplicates
        if label in quadrant_map:
            label = f"{label}_alt"

        cropped = img[y:y+h, x:x+w]
        alpha_crop = create_alpha_mask(cropped)
        b, g, r = cv2.split(cropped[:, :, :3])
        rgba = cv2.merge([b, g, r, alpha_crop])

        out_name = f"{filename}_{label}.png"
        out_path = os.path.join(OUTPUT_FOLDER, out_name)
        cv2.imwrite(out_path, rgba)

        pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).resize((200, 200))
        tk_img = ImageTk.PhotoImage(pil_img)
        lbl = Label(scroll_frame, image=tk_img, text=f"{filename}_{label}", compound="top")
        lbl.image = tk_img
        lbl.pack(pady=5)
        previews.append(tk_img)

    Button(preview_window, text="Close Preview", command=preview_window.destroy).pack(pady=10)

# === GUI LAUNCHER ===
def launch_gui():
    def select_files():
        filepaths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
        for filepath in filepaths:
            filename = os.path.splitext(os.path.basename(filepath))[0]
            img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
            detect_semantic_views(img, filename)

    root = Tk()
    root.title("Blueprint View Cropper (Semantic Layout)")
    root.geometry("300x150")

    label = Label(root, text="Select .png blueprint files with 4-view layout")
    label.pack(pady=10)

    btn = Button(root, text="Select Files", command=select_files)
    btn.pack(pady=10)

    root.mainloop()

# === RUN ===
if __name__ == "__main__":
    launch_gui()


