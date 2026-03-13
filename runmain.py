import os
import subprocess
import sys

def run_exe(relative_path):
    try:
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_directory, relative_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.endswith(".py"):
            subprocess.run([sys.executable, file_path])
        else:
            subprocess.run([file_path], shell=True)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_exe("main.py")
