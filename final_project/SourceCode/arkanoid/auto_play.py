import subprocess

commands = []
# trian
# for i in range(1, 21):
#     commands.append(f"python -m mlgame -i ./ml/ml_play_manual.py . --difficulty NORMAL --level {i}")
# test
for i in range(50, 55):
    commands.append(f"python -m mlgame -i ./ml/ml_play_manual.py . --difficulty NORMAL --level {i}")
for command in commands:
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        break
    else:
        print(f"Command succeeded with return code {result.returncode}")
