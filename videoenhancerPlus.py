import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np

def enhance_video():
    # Function to enhance the selected video
    
    # Get the file path of the input video
    file_path = file_var.get()
    
    if not file_path:
        # If the file path is empty, display an error message
        error_label.config(text="Please select a video.")
        return
    
    try:
        # Open the video file
        video = cv2.VideoCapture(file_path)
        
        # Get video properties
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create a VideoWriter object to write the enhanced video
        output_file = file_path.rsplit(".", 1)[0] + "_enhanced_Plus_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
        
        # Process each frame of the video
        for _ in range(frame_count):
            ret, frame = video.read()
            
            if ret:
                # Apply video enhancement effects to the frame
                enhanced_frame = cv2.GaussianBlur(frame, (0, 0), 2)
                enhanced_frame = cv2.addWeighted(frame, 1.5, enhanced_frame, -0.5, 0)
                enhanced_frame = cv2.convertScaleAbs(enhanced_frame, alpha=1.2, beta=10)
                #enhanced_frame = cv2.medianBlur(enhanced_frame, 5)
                #enhanced_frame = cv2.Laplacian(enhanced_frame, cv2.CV_64F)
                
                # Write the enhanced frame to the output video file
                writer.write(enhanced_frame)
        
        # Release resources
        video.release()
        writer.release()
        
        # Display success message
        error_label.config(text="Video enhanced successfully!")
        
    except Exception as e:
        # Print the error message to the terminal
        print(f"Error: {str(e)}")

def select_video():
    # Function to open the file explorer and select the video file
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
    file_var.set(file_path)

# Create the main window
window = tk.Tk()
window.title("Video Enhancer")

# File path variable
file_var = tk.StringVar()

# Select video button
select_button = tk.Button(window, text="Select Video", command=select_video)
select_button.pack()

# File path entry field
file_entry = tk.Entry(window, textvariable=file_var, state="readonly", width=50)
file_entry.pack()

# Enhance video button
enhance_button = tk.Button(window, text="Enhance Video", command=enhance_video)
enhance_button.pack()

# Error label
error_label = tk.Label(window, text="")
error_label.pack()

# Start the GUI main loop
window.mainloop()
