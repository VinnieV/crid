# RFID Client

This is a command-line interface (CLI) application for interacting with Mifare Classic 1K cards using a NFC reader.

## Installation 

Linux requires some libraries to be installed:
```bash
sudo apt-get update
sudo apt-get install libpcsclite-dev libpcsclite1 pcscd pcsc-tools
```

Installation through pip package manager
```bash
pip3 install crid
```

Installation from source
```bash
git clone https://github.com/VinnieV/crid.git
cd crid
pip3 install .
```

If the `crid` command is not available after using any of these installation methods, please review the detailed installation walkthrough below.

Executing from source:
```bash
git clone https://github.com/VinnieV/crid.git
cd crid
pip3 install -r requirements.txt
python3 main.py
```

## Usage/Examples
```bash
# Read the UID of the card
crid --read_uid

# Identify the card to the user
crid --identify

# Read a block from the card using key type A and key value ffffffffffff
crid --read_block 2 --key_type A --key_value ffffffffffff

# Write "Hello, World!" to block 3 using key type B and key value a1b2c3d4e5f6
crid --write_block 3 --data "48656C6C6F2C20576F726C6421" --key_type B --key_value a1b2c3d4e5f6

# Read sector 1 from the card using key type A and key value ffffffffffff
crid --read_sector 1 --key_type A --key_value ffffffffffff

# Read all 16 sectors from the card using key type B and key value a1b2c3d4e5f6
crid --read_full --key_type B --key_value a1b2c3d4e5f6

# Find keys for a Mifare Classic card (requires mfoc binary)
crid --find_mifare_keys

# Brute force keys for block 18 using the key list file keys.txt
crid --brute_force_keys 18 --key_list mifare_access_keys_top100.lst

# Mute the buzzer on the reader
crid --mute

# Provide the flag option
crid --flag

# Enable the buzzer on the reader
crid --beep

# Set the log level to DEBUG
crid --log_level DEBUG

# Send an APDU command to the NFC device
crid --apdu_command 00A4040007A000000003101000

# Set the data format to string
crid --data_format string
```

## API Reference
The main class in this project is RFIDClient within the `cli.py` source file which provides methods to interact with the NFC reader and the Mifare Classic 1K card.

## Detailed Installation Walkthrough

To install the RFID Client application, follow the steps below:

1. Clone the repository using the following command:
     ```bash
     git clone https://github.com/VinnieV/crid.git
     ```

2. Navigate to the cloned repository:
     ```bash
     cd crid
     ```

3. If you have Python 3 installed, pip3 should be available. If not, you can install Python 3 and pip3 by following the instructions provided in the links below:
     - [Install Python 3](https://www.python.org/downloads/)
     - [Install pip3](https://pip.pypa.io/en/stable/installing/)

4. Install the application using pip3. There are two ways to install pip packages: as a user or system-wide. Choose the appropriate method based on your requirements:

     System-wide:

     ```bash
     pip3 install .
     ```

     User-wide:

     ```bash
     pip3 install . --user
     ```

5. Add the Python Scripts directory to your PATH environment variable. This step is necessary to ensure that the `crid` binary is accessible from anywhere in the command prompt or terminal. The process for adding the Python path to the PATH variable differs between Windows and Linux:

     - **Windows**:
         - Open the Start menu and search for "Environment Variables".
         - Click on "Edit the system environment variables".
         - In the System Properties window, click on the "Environment Variables" button.
         - In the "System Variables" section, select the "Path" variable and click on "Edit".
         - Execute the following command to retrieve the path:

          ```bash
          pip3 show crid
          ```

          - Based on the Location listed there you can find the Python Scripts folder, the path should look something similar like this:

          ```bash
          c:\users\<username>\appdata\local\packages\pythonsoftwarefoundation.python.3.8_qbz5n2kfra8p0\localcache\local-packages\python38\Scripts
          ```
         - Click "OK" to save the changes.

     - **Linux**:
         - Open a terminal window.
         - Edit the `.bashrc` or `.bash_profile` file in your home directory using a text editor (e.g., `nano ~/.bashrc`).
         - Add the following line at the end of the file, replacing `<username>` with the your linux username:
          ```bash
          export PATH="/home/<username>/.local/bin/:$PATH"
          ```
         - Save the file and exit the text editor.
         - Run the following command to apply the changes:
          ```bash
          source ~/.bashrc
          ```

Once you have completed these steps, you should be able to use the RFID Client application successfully.

# Build for distributing

```bash
pip3 install --upgrade build
python3 -m build
pip3 install --upgrade twine
python3 -m twine upload dist/*
```