import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget, QFileDialog
import cv2

class VideoEnhancerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize enhancement parameters
        self.brightness = 0
        self.contrast = 1.0
        self.enhancements_enabled = False

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

        # Create buttons for control
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.play_video)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_video)

        self.toggle_button = QPushButton('Toggle Enhancements')
        self.toggle_button.clicked.connect(self.toggle_enhancements)

        # Create button for opening a video file
        self.open_button = QPushButton('Open Video')
        self.open_button.clicked.connect(self.open_video_file)

        # Create labels to display parameter values
        self.brightness_label = QLabel(f'Brightness: {self.brightness}')
        self.contrast_label = QLabel(f'Contrast: {self.contrast}')

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_player)
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.open_button)
        layout.addWidget(self.brightness_label)
        layout.addWidget(self.contrast_label)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Initialize the video capture
        self.video_capture = None

    def open_video_file(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(self, 'Open Video File', '', 'Video Files (*.mp4 *.avi)')
        if video_path:
            self.video_capture = cv2.VideoCapture(video_path)
            self.play_video()

    def play_video(self):
        if not self.video_timer.isActive():
            self.video_timer.start(33)  # Update frame every 33 milliseconds (approx. 30 FPS)
            self.play_button.setText('Pause')
        else:
            self.video_timer.stop()
            self.play_button.setText('Play')

    def stop_video(self):
        self.video_timer.stop()
        self.video_capture.release()
        self.video_player.clear()
        self.play_button.setText('Play')

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            if self.enhancements_enabled:
                # Apply enhancements (brightness, contrast, filters, etc.) to the frame using OpenCV functions
                enhanced_frame = frame  # Placeholder for actual enhancement code
                frame_rgb = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to QImage for displaying in QLabel
            height, width, channel = frame_rgb.shape
            bytes_per_line = channel * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Display the frame in the QLabel
            self.video_player.setPixmap(QPixmap.fromImage(q_image))

    def toggle_enhancements(self):
        self.enhancements_enabled = not self.enhancements_enabled

    def update_brightness(self, value):
        self.brightness = value
        self.brightness_label.setText(f'Brightness: {self.brightness}')

    def update_contrast(self, value):
        self.contrast = value / 100.0
        self.contrast_label.setText(f'Contrast: {self.contrast}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = VideoEnhancerGUI()
    gui.show()
    sys.exit(app.exec_())
