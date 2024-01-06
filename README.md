# RFID Client

This is a command-line interface (CLI) application for interacting with Mifare Classic 1K cards using a NFC reader.

## Installation

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
```

## Usage/Examples
```
python main.py --read_uid
python main.py --read_block 10
python main.py --write_block 10 --data "Hello, World!"
python main.py --read_sector 2
python main.py --read_full
python main.py --mute
python main.py --beep
```

## API Reference
The main class in this project is RFIDClient which provides methods to interact with the NFC reader and the Mifare Classic 1K card.

## Contributing
## Installation

To install the RFID Client application, follow the steps below:

1. Clone the repository using the following command:
     ```bash
     git clone https://github.com/VinnieV/crid.git
     ```

2. Navigate to the cloned repository:
     ```bash
     crid
     ```

3. If you have Python 3 installed, pip3 should be available. If not, you can install Python 3 and pip3 by following the instructions provided in the links below:
     - [Install Python 3](https://www.python.org/downloads/)
     - [Install pip3](https://pip.pypa.io/en/stable/installing/)

4. Install the application using pip3. There are two ways to install pip packages: as a user or system-wide. Choose the appropriate method based on your requirements:
    **System-wide**:
     ```bash
     pip3 install .
     ```

    **User-wide**:
     ```bash
     pip3 install . --user
     ```

5. Add the Python installation directory to your PATH environment variable. This step is necessary to ensure that the `crid` binary is accessible from anywhere in the command prompt or terminal. The process for adding the Python path to the PATH variable differs between Windows and Linux:

     - **Windows**:
         - Open the Start menu and search for "Environment Variables".
         - Click on "Edit the system environment variables".
         - In the System Properties window, click on the "Environment Variables" button.
         - In the "System Variables" section, select the "Path" variable and click on "Edit".
         - Add the path to the Python installation directory (e.g., `C:\Python39`) to the list of paths.
         - Click "OK" to save the changes.

     - **Linux**:
         - Open a terminal window.
         - Edit the `.bashrc` or `.bash_profile` file in your home directory using a text editor (e.g., `nano ~/.bashrc`).
         - Add the following line at the end of the file, replacing `/path/to/python` with the actual path to the Python installation directory:
             ```bash
             export PATH="/path/to/python:$PATH"
             ```
         - Save the file and exit the text editor.
         - Run the following command to apply the changes:
             ```bash
             source ~/.bashrc
             ```

Once you have completed these steps, you should be able to use the RFID Client application successfully.
