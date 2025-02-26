import os
import subprocess

def execute_launch_scripts():
    """Execute launch.sh script in each R<n> folder if it exists."""
    for folder in os.listdir():
        if os.path.isdir(folder) and folder.startswith("R") and folder[1:].isdigit():
            script_path = os.path.join(folder, "launch.sh")
            if os.path.exists(script_path):
                print(f"[INFO] Executing launch script in {folder}...")
                subprocess.run(["bash", script_path], check=True)
            else:
                print(f"[INFO] No launch.sh found in {folder}.")
                
if __name__ == "__main__":
    execute_launch_scripts()