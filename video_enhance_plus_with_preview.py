import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk

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
        
        # Retrieve enhancement values from sliders
        brightness_value = brightness_slider.get()
        contrast_value = contrast_slider.get()
        saturation_value = saturation_slider.get()
        sharpen_value = sharpen_slider.get()
        
        # Process each frame of the video
        for frame_index in range(frame_count):
            ret, frame = video.read()
            
            if ret:
                # Apply video enhancement effects to the frame
                enhanced_frame = cv2.convertScaleAbs(frame, alpha=contrast_value, beta=brightness_value)
                hsv_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2HSV)
                hsv_frame[:, :, 1] = hsv_frame[:, :, 1] * saturation_value
                enhanced_frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)
                
                # Apply sharpening to the frame
                sharpened_frame = cv2.filter2D(enhanced_frame, -1, sharpening_kernel * sharpen_value)
                enhanced_frame = cv2.addWeighted(enhanced_frame, 1 + sharpen_value, sharpened_frame, -sharpen_value, 0)
                
                # Write the enhanced frame to the output video file
                writer.write(enhanced_frame)
                
                # Update progress label
                progress_label.config(text=f"Processing frame {frame_index}/{frame_count - 1}")
                
                # Display the enhanced frame in the preview window
                if frame_index % preview_interval == 0:
                    preview_image = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)
                    preview_image = Image.fromarray(preview_image)
                    preview_image = ImageTk.PhotoImage(preview_image)
                    preview_label.config(image=preview_image)
                    preview_label.image = preview_image  # Keep a reference to prevent image garbage collection
                    window.update()
        
        # Release resources
        video.release()
        writer.release()
        
        # Display success message
        error_label.config(text="Video enhanced successfully!")
        progress_label.config(text="")
        
    except Exception as e:
        # Print the error message to the terminal
        print(f"Error: {str(e)}")

def select_video():
    # Function to open the file explorer and select the video file
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
    file_var.set(file_path)
    
    # Clear the preview window
    preview_label.config(image="")

def sharpen_video(value):
    # Function to update the sharpening level
    sharpen_value = sharpen_slider.get()
    sharpen_label.config(text=f"Sharpen: {sharpen_value}")

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

# Brightness slider
brightness_label = tk.Label(window, text="Brightness")
brightness_label.pack()
brightness_slider = tk.Scale(window, from_=-100, to=100, orient=tk.HORIZONTAL, length=200)
brightness_slider.pack()

# Contrast slider
contrast_label = tk.Label(window, text="Contrast")
contrast_label.pack()
contrast_slider = tk.Scale(window, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
contrast_slider.pack()

# Saturation slider
saturation_label = tk.Label(window, text="Saturation")
saturation_label.pack()
saturation_slider = tk.Scale(window, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
saturation_slider.pack()

# Sharpen slider
sharpen_label = tk.Label(window, text="Sharpen: 0")
sharpen_label.pack()
sharpen_slider = tk.Scale(window, from_=0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, length=200, command=sharpen_video)
sharpen_slider.pack()

# Enhance video button
enhance_button = tk.Button(window, text="Enhance Video", command=enhance_video)
enhance_button.pack()

# Progress label
progress_label = tk.Label(window, text="")
progress_label.pack()

# Preview window
preview_interval = 10  # Interval between preview updates (in frames)
preview_label = tk.Label(window)
preview_label.pack()

# Kernel for sharpening
sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

# Start the GUI main loop
window.mainloop()
