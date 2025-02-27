import os
import subprocess

def create_and_activate_venv():
    """Create and activate the virtual environment."""
    if not os.path.exists("venv"):
        print("[INFO] Creating virtual environment 'venv'...")
        subprocess.run(["python3", "-m", "venv", "venv"], check=True)
    else:
        print("[INFO] Virtual environment 'venv' already exists.")

    if os.name == "nt":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "source venv/bin/activate"
    
    print(f"[INFO] To activate the environment, run: {activate_script}")


def install_requirements():
    """Search and install requirements.txt files in R<n> folders."""
    venv_pip = os.path.join("venv", "bin", "pip") if os.name != "nt" else os.path.join("venv", "Scripts", "pip.exe")
    
    for folder in os.listdir():
        if os.path.isdir(folder) and folder.startswith("R") and folder[1:].isdigit():
            req_path = os.path.join(folder, "requirements.txt")
            if os.path.exists(req_path):
                print(f"[INFO] Installing dependencies from {req_path}...")
                subprocess.run([venv_pip, "install", "-r", req_path], check=True)
            else:
                print(f"[INFO] No requirements.txt found in {folder}.")
                
def execute_install_scripts():
    """Execute install.sh script in each R<n> folder if it exists."""
    for folder in os.listdir():
        if os.path.isdir(folder) and folder.startswith("R") and folder[1:].isdigit():
            script_path = os.path.join(folder, "install.sh")
            if os.path.exists(script_path):
                print(f"[INFO] Executing install script in {folder}...")
                subprocess.run(["bash", script_path], check=True)
            else:
                print(f"[INFO] No install.sh found in {folder}.")
              
if __name__ == "__main__":
    create_and_activate_venv()
    install_requirements()
    print("[INFO] Installation completed. Activate the environment and run your project!")
