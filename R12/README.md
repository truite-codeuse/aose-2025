## Platform installers and launchers

### Author

Role R12; Florian Posez

### General Description

#### Installer script
The installer Python script automates the setup of a virtual environment and the installation of dependencies for multiple project components. It performs the following tasks:

1. **Create and Activate a Virtual Environment**  
   - If a `venv` directory does not exist, the script creates a virtual environment using `python3 -m venv venv`. 

2. **Install Dependencies from `requirements.txt`**  
   - The script scans all subdirectories that follow the `R<n>` naming pattern (e.g., `R1`, `R2`, `R3`).
   - If a `requirements.txt` file is found within a directory, the script installs the required dependencies using `pip`.

3. **Execute Bash Installation Scripts (`install.sh`)**  
   - In each `R<n>` directory, if an `install.sh` script exists, the script executes it using the `bash` command.
   - This ensures that any additional setup required by individual components is completed.

4. **Completion Message**  
   - After executing all necessary installations, the script notifies the user that the setup process is complete and prompts them to activate the virtual environment before running the project.

#### Launcher script
The launcher script automates the launching of all microservices by scanning all the `R<n>` directories and executing the `launch.sh` scripts if founded
	