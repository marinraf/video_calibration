import tkinter as tk
from PIL import Image, ImageTk
import cv2
import json
import numpy as np

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

def save_config():
    updated_config = {group: {var: entry_vars[group][var].get() for var in entry_vars[group]} for group in entry_vars}
    with open('config.json', 'w') as file:
        json.dump(updated_config, file, indent=4)
    root.destroy()

def exit_app():
    root.destroy()

def update_frame():
    global cap, canvas, detected_canvas, photo, detected_photo

    ret, frame = cap.read()

    if ret:

        result_frame = np.ones((480, 640), dtype=np.uint8) * 255
        
        for area in ["area1", "area2", "area3"]:
            try:
                # Update rectangle coordinates
                left = int(entry_vars[area]['left'].get())
                right = int(entry_vars[area]['right'].get())
                up = int(entry_vars[area]['up'].get())
                down = int(entry_vars[area]['down'].get())
                threshold = int(entry_vars[area]['threshold'].get())

                if right > left and down > up:

                    # Convert the frame to grayscale
                    gray_frame = cv2.cvtColor(frame[up:down, left:right], cv2.COLOR_BGR2GRAY)

                    # If rectangle coordinates are valid, draw the rectangle
                    cv2.rectangle(frame, (left, up), (right, down), (0, 255, 0), 2)

                    # Calculate minimum luminance inside the rectangle
                    mimimum_luminance = np.min(gray_frame) if gray_frame.size > 0 else 0

                    # Calculate mean luminance inside the rectangle
                    mean_luminance = np.mean(gray_frame) if gray_frame.size > 0 else 0

                    # Calculate number of black pixels
                    gray_gaussian_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
                    detected_frame = cv2.threshold(gray_frame, threshold, 225, cv2.THRESH_BINARY_INV)[1]
                    detected_frame2 = cv2.threshold(gray_frame, threshold, 225, cv2.THRESH_BINARY)[1]
                    detected_area = cv2.countNonZero(detected_frame)

                    result_frame[up:down, left:right] = detected_frame2

                    # Put minimum luminance text on frame
                    cv2.putText(frame, "min: " + str(int(mimimum_luminance)), 
                                (left, down + 20), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.5, (0, 255, 120), 1, cv2.LINE_AA)

                    # Put mean luminance text on frame
                    cv2.putText(frame, "mean: " + str(int(mean_luminance)), 
                                (left, down + 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.5, (0, 255, 120), 1, cv2.LINE_AA)
                    
                    # Put detected pixels text on frame
                    cv2.putText(frame, "detected: " + str(int(detected_area)), 
                                (left, down + 60), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.5, (0, 255, 120), 1, cv2.LINE_AA)
            except ValueError:
                # If values are not numeric, do not draw the rectangle or calculate luminance
                pass

        # Convert the frame to PIL format and then to ImageTk format
        img = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)

        # Convert the detected frame to PIL format and then to ImageTk format
        detected_img = Image.fromarray(result_frame)
        detected_photo = ImageTk.PhotoImage(image=detected_img)
        detected_canvas.create_image(0, 0, image=detected_photo, anchor=tk.NW)
        
    root.after(10, update_frame)

# Load the config file
config = load_config()

# Create the main window
root = tk.Tk()
root.title("Config Editor and Webcam Feed")

# Dictionaries to store entry widgets and variables for each group
entry_widgets = {}
entry_vars = {}

row = 0
for group, settings in config.items():
    frame = tk.LabelFrame(root, text=group, padx=5, pady=5)
    frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
    entry_widgets[group] = {}
    entry_vars[group] = {}

    for i, (var, value) in enumerate(settings.items()):
        var_value = tk.StringVar(value=str(value))
        tk.Label(frame, text=var).grid(row=i, column=0)
        entry = tk.Entry(frame, textvariable=var_value)
        entry.grid(row=i, column=1)
        entry_widgets[group][var] = entry
        entry_vars[group][var] = var_value
    row += 1

# Add Refresh, Save and Exit buttons
tk.Button(root, text="Save and Exit", command=save_config).grid(row=row + 1, column=0)
tk.Button(root, text="Exit without Saving", command=exit_app).grid(row=row + 1, column=1)

# Webcam feed
cap = cv2.VideoCapture(0)
canvas = tk.Canvas(root, width=640, height=480)
canvas.grid(row=0, column=3, rowspan=row, padx=10, pady=10)

detected_canvas = tk.Canvas(root, width=640, height=480)
detected_canvas.grid(row=0, column=4, rowspan=row, padx=10, pady=10)

update_frame()

# Run the application
root.mainloop()

# Release the video capture object
cap.release()
