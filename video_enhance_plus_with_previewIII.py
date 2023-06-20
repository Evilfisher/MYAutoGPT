import tkinter as tk
from tkinter import filedialog
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
        self.preview_window = None

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

        preview_button = tk.Button(self.window, text="Preview", command=self.preview_video)
        preview_button.pack()

        apply_preview_button = tk.Button(self.window, text="Apply", command=self.apply_preview)
        apply_preview_button.pack()

        self.error_label = tk.Label(self.window, text="")
        self.error_label.pack()

        self.progress_label = tk.Label(self.window, text="")
        self.progress_label.pack()

        self.sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

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
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            output_file = file_path.rsplit(".", 1)[0] + "_enhanced_Plus_video.mp4"
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_file, fourcc, self.fps, (self.width, self.height))

            for _ in range(self.frame_count):
                ret, frame = self.video.read()

                if ret:
                    enhanced_frame = self.apply_enhancements(frame)
                    writer.write(enhanced_frame)

            self.video.release()
            writer.release()

            self.error_label.config(text="Video enhanced successfully!")

        except Exception as e:
            print(f"Error: {str(e)}")

    def apply_enhancements(self, frame):
        brightness_value = self.brightness_slider.get()
        contrast_value = self.contrast_slider.get()
        saturation_value = self.saturation_slider.get()
        sharpen_value = self.sharpen_slider.get()

        enhanced_frame = cv2.convertScaleAbs(frame, alpha=contrast_value, beta=brightness_value)
        hsv_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2HSV)
        hsv_frame[:, :, 1] = hsv_frame[:, :, 1] * saturation_value
        enhanced_frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)

        sharpened_frame = cv2.filter2D(enhanced_frame, -1, self.sharpening_kernel * sharpen_value)
        enhanced_frame = cv2.addWeighted(enhanced_frame, 1 + sharpen_value, sharpened_frame, -sharpen_value, 0)

        return enhanced_frame

    def preview_video(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        try:
            if self.preview_window is None:
                self.preview_window = tk.Toplevel()
                self.preview_window.title("Preview")
                self.preview_window.geometry("640x320")
                self.preview_label = tk.Label(self.preview_window)
                self.preview_label.pack()

            self.video = cv2.VideoCapture(file_path)
            self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            for frame_index in range(self.frame_count):
                ret, frame = self.video.read()

                if ret:
                    enhanced_frame = self.apply_enhancements(frame)
                    preview_frame = cv2.resize(enhanced_frame, (640, 320))
                    preview_image = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
                    preview_image = Image.fromarray(preview_image)
                    preview_image = ImageTk.PhotoImage(preview_image)
                    self.preview_label.config(image=preview_image)
                    self.preview_label.image = preview_image
                    self.preview_window.update()

            self.video.release()

        except Exception as e:
            print(f"Error: {str(e)}")

    def apply_preview(self):
        if self.preview_window is not None:
            self.preview_window.destroy()
            self.preview_window = None
            self.preview_label = None

        self.preview_video()

    def close_preview(self):
        if self.preview_window is not None:
            self.preview_window.destroy()
            self.preview_window = None
            self.preview_label = None

    def run(self):
        self.window.mainloop()

enhancer = VideoEnhancer()
enhancer.run()
