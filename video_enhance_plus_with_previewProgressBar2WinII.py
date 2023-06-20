import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
import cv2
import numpy as np
from PIL import Image, ImageTk

class VideoEnhancer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Video Enhancer")
        self.file_var = tk.StringVar()
        self.video = None
        self.frame_count = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        self.preview_window_original = None
        self.preview_window_modified = None

        self.create_widgets()

    def create_widgets(self):
        select_button = tk.Button(self.window, text="Select Video", command=self.select_video)
        select_button.pack()

        file_entry = tk.Entry(self.window, textvariable=self.file_var, state="readonly", width=50)
        file_entry.pack()

        brightness_label = tk.Label(self.window, text="Brightness")
        brightness_label.pack()
        self.brightness_slider = tk.Scale(self.window, from_=-100, to=100, orient=tk.HORIZONTAL, length=200)
        self.brightness_slider.pack()

        contrast_label = tk.Label(self.window, text="Contrast")
        contrast_label.pack()
        self.contrast_slider = tk.Scale(self.window, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.contrast_slider.pack()

        saturation_label = tk.Label(self.window, text="Saturation")
        saturation_label.pack()
        self.saturation_slider = tk.Scale(self.window, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.saturation_slider.pack()

        sharpen_label = tk.Label(self.window, text="Sharpen")
        sharpen_label.pack()
        self.sharpen_slider = tk.Scale(self.window, from_=0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.sharpen_slider.pack()

        enhance_button = tk.Button(self.window, text="Enhance Video", command=self.enhance_video)
        enhance_button.pack()

        preview_original_button = tk.Button(self.window, text="Preview Original", command=self.preview_video_original)
        preview_original_button.pack()

        preview_modified_button = tk.Button(self.window, text="Preview Modified", command=self.preview_video_modified)
        preview_modified_button.pack()

        apply_preview_button = tk.Button(self.window, text="Apply", command=self.apply_preview)
        apply_preview_button.pack()

        self.error_label = tk.Label(self.window, text="")
        self.error_label.pack()

        self.progress_label = tk.Label(self.window, text="")
        self.progress_label.pack()

        self.sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

        # Progress bar
        self.progress_bar = Progressbar(self.window, mode="determinate")
        self.progress_bar.pack()

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        self.file_var.set(file_path)
        self.close_preview()

    def enhance_video(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        try:
            self.video = cv2.VideoCapture(file_path)
            self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = int(self.video.get(cv2.CAP_PROP_FPS))
            self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.error_label.config(text="")
        except Exception as e:
            self.error_label.config(text=f"Error: {str(e)}")
            return

        self.process_video()

    def process_video(self):
        file_path = self.file_var.get()
        brightness = self.brightness_slider.get()
        contrast = self.contrast_slider.get()
        saturation = self.saturation_slider.get()
        sharpen = self.sharpen_slider.get()

        output_file_path = "enhanced_video.mp4"

        output_video = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (self.width, self.height))

        for i in range(self.frame_count):
            ret, frame = self.video.read()
            if ret:
                enhanced_frame = self.apply_enhancements(frame, brightness, contrast, saturation, sharpen)
                output_video.write(enhanced_frame)

            progress = (i + 1) / self.frame_count * 100
            self.progress_label.config(text=f"Processing: {int(progress)}%")
            self.progress_bar["value"] = progress
            self.window.update()

        output_video.release()
        self.video.release()
        self.progress_label.config(text="Processing: 100%")
        self.progress_bar["value"] = 100
        self.window.update()

        self.error_label.config(text="Video enhancement completed.")
        self.preview_video_original()

    def apply_enhancements(self, frame, brightness=0, contrast=1.0, saturation=1.0, sharpen=0.0):
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Apply brightness adjustment
        frame_rgb = self.adjust_brightness(frame_rgb, brightness)

        # Apply contrast adjustment
        frame_rgb = self.adjust_contrast(frame_rgb, contrast)

        # Apply saturation adjustment
        frame_rgb = self.adjust_saturation(frame_rgb, saturation)

        # Apply sharpening
        frame_rgb = self.sharpen(frame_rgb, sharpen)

        # Convert RGB to BGR
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        return frame_bgr

    def adjust_brightness(self, frame, value):
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, value)
        v = np.clip(v, 0, 255)
        hsv = cv2.merge((h, s, v))
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return frame

    def adjust_contrast(self, frame, value):
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.multiply(l, value)
        l = np.clip(l, 0, 255)
        lab = cv2.merge((l, a, b))
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        return frame

    def adjust_saturation(self, frame, value):
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.multiply(s, value)
        s = np.clip(s, 0, 255)
        hsv = cv2.merge((h, s, v))
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return frame

    def sharpen(self, frame, value):
        blurred = cv2.filter2D(frame, -1, self.sharpening_kernel * value)
        frame = cv2.addWeighted(frame, 1 + value, blurred, -value, 0)
        return frame

    def preview_video_original(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        self.close_preview()

        self.video = cv2.VideoCapture(file_path)
        ret, frame = self.video.read()

        if not ret:
            self.error_label.config(text="Error: Failed to read video frame.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = self.resize_image(img)
        self.preview_window_original = self.create_preview_window(img)
        self.preview_window_original.mainloop()

    def preview_video_modified(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        self.close_preview()

        self.video = cv2.VideoCapture(file_path)
        ret, frame = self.video.read()

        if not ret:
            self.error_label.config(text="Error: Failed to read video frame.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = self.apply_enhancements(frame_rgb)
        img = Image.fromarray(frame_rgb)
        img = self.resize_image(img)
        self.preview_window_modified = self.create_preview_window(img)
        self.preview_window_modified.mainloop()

    def create_preview_window(self, img):
        window = tk.Toplevel(self.window)
        window.title("Video Preview")

        canvas = tk.Canvas(window, width=img.width, height=img.height)
        canvas.pack()

        img_tk = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

        return window

    def apply_preview(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        self.close_preview()

        self.video = cv2.VideoCapture(file_path)
        ret, frame = self.video.read()

        if not ret:
            self.error_label.config(text="Error: Failed to read video frame.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = self.apply_enhancements(frame_rgb)
        img = Image.fromarray(frame_rgb)
        img = self.resize_image(img)
        self.preview_window_modified = self.create_preview_window(img)

        while ret:
            ret, frame = self.video.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = self.apply_enhancements(frame_rgb)
                img = Image.fromarray(frame_rgb)
                img = self.resize_image(img)
                img_tk = ImageTk.PhotoImage(img)
                canvas = self.preview_window_modified.winfo_children()[0]
                canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
                self.preview_window_modified.update()

        self.preview_window_modified.mainloop()

    def close_preview(self):
        if self.preview_window_original:
            self.preview_window_original.destroy()
            self.preview_window_original = None

        if self.preview_window_modified:
            self.preview_window_modified.destroy()
            self.preview_window_modified = None

    def resize_image(self, image, max_width=800, max_height=600):
        width, height = image.size

        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height))

        return image

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    enhancer = VideoEnhancer()
    enhancer.run()
