import subprocess
import tkinter as tk
def execute_commands():
    commands = []
    iterations = int(iterations_entry.get())
    AI_1P_PATH = AI_1_entry.get()
    AI_2P_PATH = AI_2_entry.get()
    DIFFICULTY = DIFFICULTY_entry.get()
    GAME_OVER_SCORE = GAME_OVER_SCORE_entry.get()
    INIT_VEL = INIT_VEL_entry.get()

    for i in range(0, iterations):
        commands.append(f"python -m mlgame -i {AI_1P_PATH} -i {AI_2P_PATH} ./ --difficulty {DIFFICULTY} --game_over_score {GAME_OVER_SCORE}  --init_vel {INIT_VEL}")
    
    for command in commands:
        result = subprocess.run(command, shell=True)

        


# Create the GUI window
window = tk.Tk()
window.title("Auto Play")
window.geometry("400x200")

# Create a label and text box for iterations
iterations_label = tk.Label(window, text="Iterations:")
iterations_label.grid(row=0, column=0, sticky="w")

iterations_entry = tk.Entry(window, width=5)
iterations_entry.insert(0, "1")  # Set the initial value to 1
iterations_entry.grid(row=0, column=1, sticky="w")

# Create a label and text box for AI_1_PATH
AI_1_label = tk.Label(window, text="AI_1_PATH:")
AI_1_label.grid(row=1, column=0, sticky="w")

AI_1_entry = tk.Entry(window, width=30)
AI_1_entry.insert(0, "./ml/ml_play_template_1P_AI.py")  # Set the initial value
AI_1_entry.grid(row=1, column=1, sticky="w")

# Create a label and text box for AI_2_PATH
AI_2_label = tk.Label(window, text="AI_2_PATH:")
AI_2_label.grid(row=2, column=0, sticky="w")

AI_2_entry = tk.Entry(window, width=30)
AI_2_entry.insert(0, "./ml/ml_play_template_2P_AI.py")  # Set the initial value
AI_2_entry.grid(row=2, column=1, sticky="w")

# Create a label and text box for DIFFICULTY
DIFFICULTY_label = tk.Label(window, text="DIFFICULTY:")
DIFFICULTY_label.grid(row=3, column=0, sticky="w")

DIFFICULTY_options = ["EASY", "NORMAL", "HARD"]  # List of difficulty options

DIFFICULTY_entry = tk.StringVar(window)
DIFFICULTY_entry.set(DIFFICULTY_options[0])  # Set the initial value to the first option

DIFFICULTY_dropdown = tk.OptionMenu(window, DIFFICULTY_entry, *DIFFICULTY_options)
DIFFICULTY_dropdown.grid(row=3, column=1, sticky="w")

# Create a label and text box for GAME_OVER_SCORE
GAME_OVER_SCORE_label = tk.Label(window, text="GAME_OVER_SCORE:")
GAME_OVER_SCORE_label.grid(row=4, column=0, sticky="w")

GAME_OVER_SCORE_entry = tk.Entry(window, width=5)
GAME_OVER_SCORE_entry.insert(0, 15)  # Set the initial value
GAME_OVER_SCORE_entry.grid(row=4, column=1, sticky="w")

# Create a label and text box for INIT_VEL
INIT_VEL_label = tk.Label(window, text="INIT_VEL:")
INIT_VEL_label.grid(row=5, column=0, sticky="w")

INIT_VEL_entry = tk.Entry(window, width=5)
INIT_VEL_entry.insert(0, 7)  # Set the initial value
INIT_VEL_entry.grid(row=5, column=1, sticky="w")


# Create a button to execute the commands
execute_button = tk.Button(window, text="Execute", command=execute_commands)
execute_button.grid(row=7, column=0)


# Start the GUI event loop
window.mainloop()
