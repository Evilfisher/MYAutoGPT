import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QCheckBox, QSlider
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
import numpy as np


class VideoEnhancerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.video_player = QLabel()
        self.open_button = QPushButton('Open Video')
        self.play_button = QPushButton('Play')
        self.stop_button = QPushButton('Stop')

        self.brightness_checkbox = QCheckBox('Brightness')
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_label = QLabel('Brightness: 0')

        self.contrast_checkbox = QCheckBox('Contrast')
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_label = QLabel('Contrast: 1.0')

        self.sharpening_checkbox = QCheckBox('Sharpening')
        self.sharpening_slider = QSlider(Qt.Horizontal)
        self.sharpening_label = QLabel('Sharpening: 0')

        self.color_checkbox = QCheckBox('Color')
        self.color_slider = QSlider(Qt.Horizontal)
        self.color_label = QLabel('Color: 0')

        self.saturation_checkbox = QCheckBox('Saturation')
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_label = QLabel('Saturation: 1.0')

        self.hue_checkbox = QCheckBox('Hue')
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_label = QLabel('Hue: 0')

        self.video_timer = QTimer()
        self.brightness = 0
        self.contrast = 1.0
        self.sharpening = 0
        self.color = 0
        self.saturation = 1.0
        self.hue = 0

        self.initialize_ui()

    def initialize_ui(self):
        self.open_button.clicked.connect(self.open_video_file)
        self.play_button.clicked.connect(self.play_video)
        self.stop_button.clicked.connect(self.stop_video)

        self.brightness_checkbox.stateChanged.connect(self.update_brightness)
        self.brightness_slider.valueChanged.connect(self.update_brightness)

        self.contrast_checkbox.stateChanged.connect(self.update_contrast)
        self.contrast_slider.valueChanged.connect(self.update_contrast)

        self.sharpening_checkbox.stateChanged.connect(self.update_sharpening)
        self.sharpening_slider.valueChanged.connect(self.update_sharpening)

        self.color_checkbox.stateChanged.connect(self.update_color)
        self.color_slider.valueChanged.connect(self.update_color)

        self.saturation_checkbox.stateChanged.connect(self.update_saturation)
        self.saturation_slider.valueChanged.connect(self.update_saturation)

        self.hue_checkbox.stateChanged.connect(self.update_hue)
        self.hue_slider.valueChanged.connect(self.update_hue)

        self.video_timer.timeout.connect(self.update_frame)

        layout = QVBoxLayout()
        layout.addWidget(self.video_player)
        layout.addWidget(self.open_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)

        layout.addWidget(self.brightness_checkbox)
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.brightness_label)

        layout.addWidget(self.contrast_checkbox)
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.contrast_label)

        layout.addWidget(self.sharpening_checkbox)
        layout.addWidget(self.sharpening_slider)
        layout.addWidget(self.sharpening_label)

        layout.addWidget(self.color_checkbox)
        layout.addWidget(self.color_slider)
        layout.addWidget(self.color_label)

        layout.addWidget(self.saturation_checkbox)
        layout.addWidget(self.saturation_slider)
        layout.addWidget(self.saturation_label)

        layout.addWidget(self.hue_checkbox)
        layout.addWidget(self.hue_slider)
        layout.addWidget(self.hue_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_video_file(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(self, 'Open Video File', '', 'Video Files (*.mp4 *.avi)')
        if video_path:
            self.video_capture = cv2.VideoCapture(video_path)
            self.frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.play_video()

    def play_video(self):
        self.video_timer.start(33)

    def stop_video(self):
        self.video_timer.stop()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            enhanced_frame = self.apply_enhancements(frame)
            image = self.convert_image(enhanced_frame)
            self.video_player.setPixmap(QPixmap.fromImage(image))

    def apply_enhancements(self, frame):
        # Apply brightness adjustment if checkbox is checked
        if self.brightness_checkbox.isChecked():
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame[:, :, 2] = cv2.add(hsv_frame[:, :, 2], self.brightness)
            frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)

        # Apply contrast adjustment if checkbox is checked
        if self.contrast_checkbox.isChecked():
            frame = cv2.multiply(frame, self.contrast)

        # Apply sharpening adjustment if checkbox is checked
        if self.sharpening_checkbox.isChecked() and self.sharpening != 0:
            kernel = np.array([[0, -1, 0], [-1, 5 + self.sharpening, -1], [0, -1, 0]], dtype=np.float32)
            frame = cv2.filter2D(frame, -1, kernel)

        # Apply color adjustment if checkbox is checked
        if self.color_checkbox.isChecked():
            frame = cv2.add(frame, self.color)

        # Apply saturation adjustment if checkbox is checked
        if self.saturation_checkbox.isChecked() and self.saturation != 1.0:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame[:, :, 1] = cv2.multiply(hsv_frame[:, :, 1], self.saturation)
            frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)

        # Apply hue adjustment if checkbox is checked
        if self.hue_checkbox.isChecked() and self.hue != 0:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame[:, :, 0] = (hsv_frame[:, :, 0] + self.hue) % 180
            frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)

        return frame

    def convert_image(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        return image

    def update_brightness(self, value):
        self.brightness = value
        self.brightness_label.setText(f'Brightness: {self.brightness}')

    def update_contrast(self, value):
        self.contrast = value / 100.0
        self.contrast_label.setText(f'Contrast: {self.contrast}')

    def update_sharpening(self, value):
        self.sharpening = value - 5
        self.sharpening_label.setText(f'Sharpening: {self.sharpening}')

    def update_color(self, value):
        self.color = value
        self.color_label.setText(f'Color: {self.color}')

    def update_saturation(self, value):
        self.saturation = value / 100.0
        self.saturation_label.setText(f'Saturation: {self.saturation}')

    def update_hue(self, value):
        self.hue = value
        self.hue_label.setText(f'Hue: {self.hue}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = VideoEnhancerGUI()
    gui.show()
    sys.exit(app.exec_())
