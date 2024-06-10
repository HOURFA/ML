import subprocess
import tkinter as tk
from tkinter import filedialog
import threading
from visualizetion import heatmap, linechart, histogram
from PIL import Image, ImageTk
import json

# Load configuration from JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

elements = config['elements']
window_title = config.get('title', 'GUI Application')

tk_img = None
result_label = None
thread = None
stop_thread = False

HEATMAP = 0
LINECHART = 1
HISTOGRAM = 2

def execute_commands():
    global stop_thread
    commands = []
    AI_1P_PATH = labels_entries["AI_1_PATH"].get()
    AI_2P_PATH = labels_entries["AI_2_PATH"].get()
    AI_3P_PATH = labels_entries["AI_3_PATH"].get()
    AI_4P_PATH = labels_entries["AI_4_PATH"].get()
    GREEN_TEAM_NUM = labels_entries["GREEN_TEAM_NUM"].get()
    BLUE_TEAM_NUM = labels_entries["BLUE_TEAM_NUM"].get()
    FRAME_LIMIT = labels_entries["FRAME_LIMIT"].get()
    FPS = labels_entries["FPS"].get()    
    # commands.append(f"python -m mlgame -f {FPS} -i {AI_1P_PATH} -i {AI_2P_PATH} -i {AI_3P_PATH} -i {AI_4P_PATH} . --green_team_num {GREEN_TEAM_NUM} --blue_team_num {BLUE_TEAM_NUM} --frame_limit {FRAME_LIMIT} --is_manual \"\"")        
    commands.append(f"python -m mlgame -f {FPS} -i {AI_1P_PATH} -i {AI_2P_PATH} . --green_team_num {GREEN_TEAM_NUM} --blue_team_num {BLUE_TEAM_NUM} --frame_limit {FRAME_LIMIT} --is_manual \"1\"")        
    
    for command in commands:
        if stop_thread:
            break
        subprocess.run(command, shell=True)

def execute_commands_thread():
    global thread, stop_thread
    stop_thread = False
    thread = threading.Thread(target=execute_commands)
    thread.start()

def stop_commands_thread():
    global stop_thread
    stop_thread = True
    if thread:
        thread.join()  # Wait for the thread to finish

def put_image(file, type):
    global tk_img, result_label
    if type == HEATMAP:
        heatmap(file)
        image = Image.open('heatmap.jpg')
    elif type == LINECHART:
        linechart(file)
        image = Image.open('linechart.jpg')
    elif type == HISTOGRAM:
        histogram(file)
        image = Image.open('histogram.jpg')
    tk_img = ImageTk.PhotoImage(image)

    if result_label is None:
        result_label = tk.Label(window, image=tk_img, bg='#f0f0f0')
        result_label.grid(row=0, column=4, columnspan=4, rowspan=200, padx=10, pady=10)
    else:
        result_label.config(image=tk_img)
        result_label.image = tk_img  # keep a reference to avoid garbage collection

def choose_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[('Python Files', '*.py')])
    entry.delete(0, tk.END)
    entry.insert(0, "/".join(file_path.split("/")[-2:]))

command_mapping = {
    "execute_commands_thread": execute_commands_thread,
    "stop_commands_thread": stop_commands_thread
}
# Create the GUI window
window = tk.Tk()
window.title(window_title)
# Add title label
title_label = tk.Label(window, text=window_title, font=("Helvetica", 24, "bold"), bg="#f0f0f0")
title_label.grid(row=0, column=0, columnspan=2, pady=20)

# Create GUI elements from the JSON configuration
labels_entries = {}
for i, element in enumerate(elements):
    if element['type'] == 'label':
        label_text = element['text']
        default_value = element['default']
        variable_name = label_text.rstrip(':')
        label = tk.Label(window, text=label_text, font=("Helvetica", 12), bg="#f0f0f0")
        label.grid(row=i+1, column=0, sticky="w", padx=10)

        if element["choose_file"]:
            var = tk.StringVar(window)
            var.set(default_value)
            entry = tk.Entry(window, width=30, font=("Helvetica", 12))
            entry.insert(0, default_value)
            entry.grid(row=i+1, column=1, sticky="w", padx=10, pady=5)
            labels_entries[variable_name] = entry
            button = tk.Button(window, text="Choose file", command=lambda v=entry: choose_file(v), font=("Helvetica", 12))
            button.grid(row=i+1, column=2, sticky="w", padx=10, pady=5)
        else:
            entry = tk.Entry(window, width=30, font=("Helvetica", 12))
            entry.insert(0, default_value)
            entry.grid(row=i+1, column=1, sticky="w", padx=10, pady=5)
            labels_entries[variable_name] = entry

    elif element['type'] == 'dropdown':
        label_text = element['label']
        options = element['options']
        default_value = element['default']
        
        label = tk.Label(window, text=label_text, font=("Helvetica", 12), bg="#f0f0f0")
        label.grid(row=i+1, column=0, sticky="w", padx=10, pady=5)
        
        var = tk.StringVar(window)
        var.set(default_value)
        
        dropdown = tk.OptionMenu(window, var, *options)
        dropdown.config(font=("Helvetica", 12))
        dropdown.grid(row=i+1, column=1, sticky="w", padx=10, pady=5)
        
        labels_entries[label_text] = var

    elif element['type'] == 'file':
        label_text = element['label']
        button_text = element['button_text']
        visualize_text = element['visualize_text']
        image_type = element['image_type']
        
        label = tk.Label(window, text=label_text, font=("Helvetica", 12), bg="#f0f0f0")
        label.grid(row=i+1, column=0, sticky="w", padx=10)
        
        var = tk.StringVar(window)
        button = tk.Button(window, text=button_text, command=lambda v=var: choose_file(v), font=("Helvetica", 12))
        button.grid(row=i+1, column=1, sticky="w", padx=10, pady=5)
        
        visualize_button = tk.Button(window, text=visualize_text, command=lambda v=var, h=image_type: put_image(v.get(), h), font=("Helvetica", 12), bg="#2196F3", fg="white")
        visualize_button.grid(row=i+1, column=2, padx=10, pady=5)
        
        labels_entries[label_text] = var

    elif element['type'] == 'button':
        button_text = element['text']
        command = command_mapping[element['command']]
        button = tk.Button(window, text=button_text, command=command, font=("Helvetica", 12), bg=element['bg'], fg=element['fg'])        
        button.grid(row=i+1, column=1, padx=10, pady=5)

# Start the GUI event loop
window.mainloop()
