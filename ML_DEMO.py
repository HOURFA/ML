import tkinter as tk
from tkinter import filedialog
import json
import subprocess
import threading
from src.visualizetion import heatmap, linechart, histogram
from PIL import Image, ImageTk
import os
from src.Rounded import RoundedButton, RoundedDropdown
from src.utils import combined_dataset
import time
tk_img = None
result_label = None
thread = None
stop_thread = False
HEATMAP = 0
LINECHART = 1
HISTOGRAM = 2
BACKGROUND_COLOR = "#9DC8C8"
FRAME_COLOR = "#519D9E"
BUTTON_COLOR = "#58C9B9"
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40


with open("config.json", "r") as file:
    config = json.load(file)

def load_config(game):
    global config

    if game == "PingPong":
        game_config = config["game"][0]
    elif game == "TankMan":
        game_config = config["game"][1]
    return game_config

def create_gui():
    global labels_entries, game_config, game_var, canvas, output_text
    window.geometry("1660x1000")
    window.configure(bg = BACKGROUND_COLOR)

    elements = game_config['elements']
    for widget in window.winfo_children():
        widget.destroy()

    game_var = tk.StringVar(window)
    game_var.set(game_config["title"])
    games = ["PingPong", "TankMan"]
    game_dropdown = RoundedDropdown(master =window,
                                    options=games,
                                    text = game_config["title"],                                    
                                    btnbackground=BUTTON_COLOR ,btnforeground="#ffffff", 
                                    selected=on_game_select, 
                                    width=500, height=50, radius=150,
                                    font=("Comic Sans MS", 60))
    game_dropdown.grid(row=0, column=0,columnspan=8, padx=10, pady=10, sticky = "nsew")

    # Create a frame to hold the form elements

    form_frame = tk.Frame(window, bg=FRAME_COLOR, bd=2, relief="groove")
    form_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
    canvas_frame = tk.Frame(window, bg=FRAME_COLOR, bd=2, relief="groove")
    canvas_frame.grid(row=1, column=4, columnspan=4, rowspan=200, padx=10, pady=10, sticky='nsew')
    output_frame = tk.Frame(window, bg=FRAME_COLOR, bd=2, relief="groove")
    output_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky= tk.S)
    
    # Create GUI elements from the JSON configuration
    labels_entries = {}
    i = 0
    button_num = 0 
    for _, element in enumerate(elements):
        i+=1
        if element['type'] == 'label':
            label_text = element['text']
            default_value = element['default']
            variable_name = label_text.rstrip(':')
            label = tk.Label(form_frame, text=label_text, font=("Comic Sans MS", 12), bg=FRAME_COLOR, fg="white")
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if element.get("text_entry"):
                entry = tk.Entry(form_frame, width=30, font=("Comic Sans MS", 12), bg=FRAME_COLOR, fg="white")
                entry.insert(0, default_value)
                entry.grid(row=i, column=1, sticky="w", padx=10, pady=5)
                labels_entries[variable_name] = entry
            if element.get("choose_file"):
                button = RoundedButton(form_frame,
                          text="Choose File",
                          font=("Comic Sans MS", 12), 
                          radius=45, 
                          btnbackground=BUTTON_COLOR, 
                          btnforeground="#ffffff", 
                          clicked=lambda e=entry: choose_file(e), 
                          width=BUTTON_WIDTH, 
                          height=BUTTON_HEIGHT)
                button.grid(row=i, column=2, sticky="w", padx=10, pady=5)
            elif element.get("choose_dir"):
                button = RoundedButton(form_frame,
                          text="Choose Dir",
                          font=("Comic Sans MS", 12), 
                          radius=45, 
                          btnbackground=BUTTON_COLOR, 
                          btnforeground="#ffffff", 
                          clicked=lambda e=entry: choose_dir(e), 
                          width=BUTTON_WIDTH, 
                          height=BUTTON_HEIGHT)
                button.grid(row=i, column=2, sticky="w", padx=10, pady=5)
            elif element.get("dropdown"):
                var = tk.StringVar(form_frame)
                var.set(default_value)
                button = RoundedDropdown(master =form_frame,
                                    options=element["options"],
                                    text = default_value,                                    
                                    btnbackground=BUTTON_COLOR ,btnforeground="#ffffff", 
                                    selected=var.set, 
                                    width=BUTTON_WIDTH, height=BUTTON_HEIGHT, radius=45,
                                    font=("Comic Sans MS", 12))
                labels_entries[label_text] = var
                button.grid(row=i, column=2, sticky="w", padx=10, pady=5)

        elif element['type'] == 'dropdown':
            label_text = element['label']
            options = element['options']
            default_value = element['default']
            
            label = tk.Label(form_frame, text=label_text, font=("Comic Sans MS", 12), bg=FRAME_COLOR, fg="white", relief="flat")
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            
            var = tk.StringVar(form_frame)
            var.set(default_value)
            
            dropdown = RoundedDropdown(master =form_frame,
                                    options=options,
                                    text = label_text,                                    
                                    btnbackground=BUTTON_COLOR ,btnforeground="#ffffff", 
                                    selected=var.set, 
                                    width=BUTTON_WIDTH, height=BUTTON_HEIGHT, radius=45,
                                    font=("Comic Sans MS", 12))
            dropdown.grid(row=i, column=1, sticky="w", padx=10, pady=5)
            
            labels_entries[label_text] = var

        elif element['type'] == 'file':
            label_text = element['label']
            button_text = element['button_text']
            visualize_text = element['visualize_text']
            image_type = element['image_type']
            default_value = element['default']
            
            label = tk.Label(form_frame, text=label_text, font=("Comic Sans MS", 12), bg=FRAME_COLOR, fg="white", relief="flat")
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)            
            entry = tk.Entry(form_frame, width=30, font=("Comic Sans MS", 12), bg=FRAME_COLOR, fg="white")
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, sticky="w", padx=10, pady=5)

            button = RoundedButton(form_frame,
                          text=button_text,
                          font=("Comic Sans MS", 12), 
                          radius=45, 
                          btnbackground=BUTTON_COLOR, 
                          btnforeground="#ffffff", 
                          clicked=lambda e=entry: choose_file(e), 
                          width=BUTTON_WIDTH, 
                          height=BUTTON_HEIGHT)
            button.grid(row=i, column=2, sticky="w", padx=10, pady=5)
            
            visualize_button = RoundedButton(form_frame,
                          text=visualize_text,
                          font=("Comic Sans MS", 12), 
                          radius=45, 
                          btnbackground=BUTTON_COLOR, 
                          btnforeground="#ffffff", 
                          clicked=lambda e=entry, h=image_type: put_image(e.get(), h), 
                          width=BUTTON_WIDTH, 
                          height=BUTTON_HEIGHT)
            visualize_button.grid(row=i, column=3, padx=10, pady=5)
            labels_entries[label_text] = entry

        elif element['type'] == 'button':
             
            button_text = element['text']
            command = command_mapping[element['command']]
            button = RoundedButton(form_frame,
                                   text=button_text,
                                   font=("Comic Sans MS", 12), 
                                   radius=45, 
                                   btnbackground=BUTTON_COLOR, 
                                   btnforeground="#ffffff",
                                   clicked=command, 
                                   width=BUTTON_WIDTH, 
                                   height=BUTTON_HEIGHT)
            button.grid(row=i, column=button_num, padx=10, pady=5)
            i -= 1
            button_num += 1
    
    canvas = tk.Canvas(canvas_frame, bg=FRAME_COLOR, width=800, height=800)
    canvas.pack(side="top", fill="both", expand=True)
    

    h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
    h_scrollbar.pack(side="bottom", fill="x")
    canvas.config(xscrollcommand=h_scrollbar.set)

    output_text = tk.Text(output_frame, font=("Comic Sans MS", 12), bg=FRAME_COLOR, fg="#ffffff", height=10)
    output_text.pack(side = "bottom", expand=True, fill="both")
def execute_commands():
    global stop_thread, labels_entries, game_config, output_text
    output_text.insert(tk.END, "----------GAME STARTED----------\n")
    output_text.see(tk.END)
    output_text.update_idletasks()    
    commands = []
    parameters = []
    command = "python -m mlgame"
    Iterations = int(labels_entries["Iterations"].get())
    for parameter in enumerate(game_config['parameters']):
        var = labels_entries[parameter[1]].get()
        parameters.append(var)
    for i in range(0, len(game_config['options'])):
        if i == game_config['test']:
            extra_options = " ./ " + game_config['options'][i] + " " + parameters[i]
        else:
            extra_options = game_config['options'][i] + " " + parameters[i]
        command = command + " " + extra_options
    for _ in range(0, Iterations):
        commands.append(command)    
    for command in commands:
        # subprocess.run(command, shell=True)
        if stop_thread:
            break
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in iter(proc.stdout.readline, ''):
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
            output_text.update_idletasks()
        for line in iter(proc.stderr.readline, ''):
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
            output_text.update_idletasks()
        proc.terminate()   
    output_text.insert(tk.END, "----------GAME FINISHED----------\n")
    output_text.see(tk.END)
    output_text.update_idletasks()


def execute_commands_thread():
    global thread, stop_thread
    stop_thread = False
    thread = threading.Thread(target=execute_commands)
    thread.start()
def combined():
    global labels_entries, output_text
    output_text.insert(tk.END, "----------COMBINED STARTED----------\n")
    output_text.see(tk.END)
    output_text.update_idletasks()
    combined_dataset(labels_entries['COMBINED_MODEL_PATH'].get(), labels_entries['COMBINED_MODEL_NAME'].get())
    output_text.insert(tk.END, "----------COMBINED FINISHED----------\n")
    output_text.see(tk.END)
    output_text.update_idletasks()
def stop_commands_thread():
    global stop_thread
    stop_thread = True
    if thread:
        thread._delete()

def choose_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)
def choose_dir(entry):
    file_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)
def put_image(file, type):    
    global tk_img, result_label, game_config, canvas
    if len(game_config["model"]) > 1: 
        file_name = os.path.basename(file)
        model_keys = list(game_config["model"].keys())
        for i in range(0, len(game_config["model"])):
            if model_keys[i] in file_name:             
                model_key = model_keys[i]
    else:
        model_key = list(game_config["model"].keys())[0]
    visualize_data = game_config['model'][model_key]['visualize_data']
    output_text.insert(tk.END, "----------VISUALIE DATA STARTED----------\n")
    output_text.see(tk.END)
    output_text.update_idletasks()
    if type == HEATMAP:
        heatmap(file,visualize_data["heatmap"])
        image = Image.open('heatmap.jpg')
    elif type == LINECHART:
        linechart(file,visualize_data["linechart"])
        image = Image.open('linechart.jpg')
    elif type == HISTOGRAM:
        histogram(file,visualize_data["histogram"])
        image = Image.open('histogram.jpg')

    tk_img = ImageTk.PhotoImage(image.resize((int(image.width), int(image.height * 0.8))))
    canvas.create_image(0, 0, anchor='nw', image=tk_img)
    canvas.config(scrollregion=canvas.bbox('all'))
    output_text.insert(tk.END, "----------VISUALIE DATA FINISHED----------\n")
    output_text.see(tk.END)
    output_text.update_idletasks()

def on_game_select(selected):
    global game_config, game_var
    game_config = load_config(selected)
    create_gui()

# Create the GUI window
window = tk.Tk()
window.title("ML Game DEMO")
window.configure(bg=BACKGROUND_COLOR)

# Create game selection dropdown
game_var = tk.StringVar(window)
game_var.set("ML Game DEMO")

games = ["PingPong", "TankMan"]
game_dropdown = tk.OptionMenu(window, game_var, *games, command=on_game_select)
game_dropdown.config(font=("Comic Sans MS", 40), bg=BUTTON_COLOR, fg="white", relief="flat")
game_dropdown.grid(row=0, column=0, sticky = "nsew")

command_mapping = {
    "execute_commands_thread": execute_commands_thread,
    "stop_commands_thread": stop_commands_thread,
    "combined" : combined
}

window.mainloop()