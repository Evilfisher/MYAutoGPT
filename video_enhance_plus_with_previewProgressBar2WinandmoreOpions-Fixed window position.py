import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk

class VideoEnhancer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Video Enhancer")

        self.create_widgets()

        self.preview_window_original = None
        self.preview_window_modified = None

        self.sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

    def create_widgets(self):
        # Select video button
        select_button = tk.Button(self.window, text="Select Video", command=self.select_video)
        select_button.pack()

        # File path entry field
        self.file_var = tk.StringVar()
        file_entry = tk.Entry(self.window, textvariable=self.file_var, state="readonly", width=50)
        file_entry.pack()

        # Enhance video button
        enhance_button = tk.Button(self.window, text="Enhance Video", command=self.enhance_video)
        enhance_button.pack()

        # Error label
        self.error_label = tk.Label(self.window, text="")
        self.error_label.pack()

        # Brightness slider
        self.brightness_slider = tk.Scale(
            self.window,
            from_=-100,
            to=100,
            resolution=1,
            orient=tk.HORIZONTAL,
            label="Brightness",
            length=200,
            command=self.update_preview_modified
        )
        self.brightness_slider.set(0)
        self.brightness_slider.pack()

        # Contrast slider
        self.contrast_slider = tk.Scale(
            self.window,
            from_=-100,
            to=100,
            resolution=1,
            orient=tk.HORIZONTAL,
            label="Contrast",
            length=200,
            command=self.update_preview_modified
        )
        self.contrast_slider.set(0)
        self.contrast_slider.pack()

        # Saturation slider
        self.saturation_slider = tk.Scale(
            self.window,
            from_=0.0,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            label="Saturation",
            length=200,
            command=self.update_preview_modified
        )
        self.saturation_slider.set(1.0)
        self.saturation_slider.pack()

        # Color slider
        self.color_slider = tk.Scale(
            self.window,
            from_=0.0,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            label="Color",
            length=200,
            command=self.update_preview_modified
        )
        self.color_slider.set(1.0)
        self.color_slider.pack()

        # Sharpen slider
        self.sharpen_slider = tk.Scale(
            self.window,
            from_=-1.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            label="Sharpen",
            length=200,
            command=self.update_preview_modified
        )
        self.sharpen_slider.set(0.0)
        self.sharpen_slider.pack()

        # Preview Original button
        preview_original_button = tk.Button(self.window, text="Preview Original", command=self.preview_video_original)
        preview_original_button.pack()

        # Preview Modified button
        preview_modified_button = tk.Button(self.window, text="Preview Modified", command=self.preview_video_modified)
        preview_modified_button.pack()

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        self.file_var.set(file_path)

    def enhance_video(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        try:
            video = cv2.VideoCapture(file_path)

            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video.get(cv2.CAP_PROP_FPS)
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            output_file = file_path.rsplit(".", 1)[0] + "_enhanced_video.mp4"
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

            for _ in range(frame_count):
                ret, frame = video.read()

                if ret:
                    enhanced_frame = self.apply_enhancements(frame)
                    writer.write(enhanced_frame)

            video.release()
            writer.release()

            self.error_label.config(text="Video enhanced successfully!")

        except Exception as e:
            print(f"Error: {str(e)}")

    def apply_enhancements(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Apply enhancements
        brightness = self.brightness_slider.get()
        contrast = self.contrast_slider.get()
        saturation = self.saturation_slider.get()
        color = self.color_slider.get()
        sharpen = self.sharpen_slider.get()

        frame = cv2.convertScaleAbs(frame, alpha=contrast * 0.01, beta=brightness)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.convertScaleAbs(frame, alpha=saturation, beta=0)
        frame = cv2.convertScaleAbs(frame, alpha=color, beta=0)

        sharpened_frame = cv2.filter2D(frame, -1, self.sharpening_kernel * sharpen)
        frame = cv2.addWeighted(frame, 1.0, sharpened_frame, 1.0, 0.0)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return frame

    def preview_video_original(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        try:
            if self.preview_window_original is not None:
                self.preview_window_original.destroy()
                self.preview_window_original = None

            video = cv2.VideoCapture(file_path)
            _, frame = video.read()

            if frame is not None:
                frame = cv2.resize(frame, (640, 320))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                image = Image.fromarray(frame)
                image_tk = ImageTk.PhotoImage(image)

                self.preview_window_original = tk.Toplevel(self.window)
                self.preview_window_original.title("Preview Original")
                preview_label = tk.Label(self.preview_window_original, image=image_tk)
                preview_label.image = image_tk
                preview_label.pack()

            video.release()

        except Exception as e:
            print(f"Error: {str(e)}")

    def preview_video_modified(self):
        file_path = self.file_var.get()

        if not file_path:
            self.error_label.config(text="Please select a video.")
            return

        try:
            if self.preview_window_modified is not None:
                self.preview_window_modified.destroy()
                self.preview_window_modified = None

            video = cv2.VideoCapture(file_path)
            _, frame = video.read()

            if frame is not None:
                frame = cv2.resize(frame, (640, 320))
                enhanced_frame = self.apply_enhancements(frame)

                image = Image.fromarray(enhanced_frame)
                image_tk = ImageTk.PhotoImage(image)

                self.preview_window_modified = tk.Toplevel(self.window)
                self.preview_window_modified.title("Preview Modified")
                preview_label = tk.Label(self.preview_window_modified, image=image_tk)
                preview_label.image = image_tk
                preview_label.pack()

            video.release()

        except Exception as e:
            print(f"Error: {str(e)}")

    def update_preview_modified(self, _):
        if self.preview_window_modified is not None:
            self.preview_video_modified()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    enhancer = VideoEnhancer()
    enhancer.run()
