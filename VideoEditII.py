import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget, QFileDialog, QCheckBox
import cv2
import numpy as np

class VideoEnhancerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize enhancement parameters
        self.brightness = 0
        self.contrast = 1.0
        self.sharpening = 0

        # Set up the video player
        self.video_player = QLabel(self)
        self.video_player.setAlignment(Qt.AlignCenter)
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.update_frame)

        # Create sliders for enhancement parameters
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.valueChanged.connect(self.update_brightness)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.valueChanged.connect(self.update_contrast)

        self.sharpening_slider = QSlider(Qt.Horizontal)
        self.sharpening_slider.valueChanged.connect(self.update_sharpening)

        # Create checkboxes for enabling/disabling enhancements
        self.brightness_checkbox = QCheckBox('Brightness')
        self.brightness_checkbox.setChecked(True)
        self.brightness_checkbox.stateChanged.connect(self.toggle_brightness)

        self.contrast_checkbox = QCheckBox('Contrast')
        self.contrast_checkbox.setChecked(True)
        self.contrast_checkbox.stateChanged.connect(self.toggle_contrast)

        self.sharpening_checkbox = QCheckBox('Sharpening')
        self.sharpening_checkbox.setChecked(True)
        self.sharpening_checkbox.stateChanged.connect(self.toggle_sharpening)

        # Create buttons for control
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.play_video)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_video)

        # Create button for opening a video file
        self.open_button = QPushButton('Open Video')
        self.open_button.clicked.connect(self.open_video_file)

        # Create labels to display parameter values
        self.brightness_label = QLabel(f'Brightness: {self.brightness}')
        self.contrast_label = QLabel(f'Contrast: {self.contrast}')
        self.sharpening_label = QLabel(f'Sharpening: {self.sharpening}')

        # Create a slider for video control
        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.sliderPressed.connect(self.pause_video)
        self.video_slider.sliderReleased.connect(self.seek_video)
        self.video_slider.setEnabled(False)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_player)
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.brightness_checkbox)
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.contrast_checkbox)
        layout.addWidget(self.sharpening_slider)
        layout.addWidget(self.sharpening_checkbox)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.open_button)
        layout.addWidget(self.brightness_label)
        layout.addWidget(self.contrast_label)
        layout.addWidget(self.sharpening_label)
        layout.addWidget(self.video_slider)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Initialize the video capture and other variables
        self.video_capture = None
        self.frame_count = 0
        self.frame_position = 0

    def open_video_file(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(self, 'Open Video File', '', 'Video Files (*.mp4 *.avi)')
        if video_path:
            self.video_capture = cv2.VideoCapture(video_path)
            self.frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_slider.setMinimum(0)
            self.video_slider.setMaximum(self.frame_count - 1)
            self.video_slider.setEnabled(True)
            self.play_video()

    def play_video(self):
        if not self.video_timer.isActive():
            self.video_timer.start(33)  # Update frame every 33 milliseconds (approx. 30 FPS)
            self.play_button.setText('Pause')
        else:
            self.video_timer.stop()
            self.play_button.setText('Play')

    def pause_video(self):
        self.video_timer.stop()

    def stop_video(self):
        self.video_timer.stop()
        self.video_capture.release()
        self.video_player.clear()
        self.play_button.setText('Play')

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            self.frame_position = int(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES))
            self.video_slider.setValue(self.frame_position)

            # Apply enhancements to the frame using OpenCV functions
            enhanced_frame = self.apply_enhancements(frame)

            # Convert the frame to QImage for displaying in QLabel
            height, width, channel = enhanced_frame.shape
            bytes_per_line = channel * width
            q_image = QImage(enhanced_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Display the frame in the QLabel
            self.video_player.setPixmap(QPixmap.fromImage(q_image))

            if self.frame_position == self.frame_count - 1:
                self.stop_video()

    def apply_enhancements(self, frame):
        # Apply enhancements (brightness, contrast, sharpening, etc.) to the frame using OpenCV functions
        enhanced_frame = frame.copy()

        # Apply brightness adjustment if checkbox is checked
        if self.brightness_checkbox.isChecked():
            enhanced_frame = cv2.add(enhanced_frame, self.brightness)

        # Apply contrast adjustment if checkbox is checked
        if self.contrast_checkbox.isChecked():
            enhanced_frame = cv2.multiply(enhanced_frame, self.contrast)

        # Apply sharpening if checkbox is checked
        if self.sharpening_checkbox.isChecked() and self.sharpening > 0:
            kernel = np.array([[0, -1, 0], [-1, 5 + self.sharpening, -1], [0, -1, 0]], dtype=np.float32)
            enhanced_frame = cv2.filter2D(enhanced_frame, -1, kernel)

        return enhanced_frame

    def update_brightness(self, value):
        self.brightness = value
        self.brightness_label.setText(f'Brightness: {self.brightness}')

    def update_contrast(self, value):
        self.contrast = value / 100.0
        self.contrast_label.setText(f'Contrast: {self.contrast}')

    def update_sharpening(self, value):
        self.sharpening = value
        self.sharpening_label.setText(f'Sharpening: {self.sharpening}')

    def toggle_brightness(self, state):
        self.brightness_slider.setEnabled(state)

    def toggle_contrast(self, state):
        self.contrast_slider.setEnabled(state)

    def toggle_sharpening(self, state):
        self.sharpening_slider.setEnabled(state)

    def seek_video(self):
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.video_slider.value())
        self.frame_position = self.video_slider.value()
        self.video_timer.start(33)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = VideoEnhancerGUI()
    gui.show()
    sys.exit(app.exec_())
