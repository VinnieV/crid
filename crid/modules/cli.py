# cli.py
import logging
import py122u.nfc as nfc
import py122u as py122u
from tabulate import tabulate
from termcolor import colored
import sys
import argparse
import os
import subprocess
import platform
import progressbar
import binascii
import time
import shutil
import datetime

class RFIDClient:
    def __init__(self):
        # Constants
        self.KeyTypes = {    
            "A": 0x60,
            "B": 0x61
        }
        self.KeyLocation = {
            "A": 0x00,
            "B": 0x01
        }

        self.COMMON_KEYS = [
            [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
            [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5],
            [0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5],
            [0x4D, 0x3A, 0x99, 0xC3, 0x51, 0xDD],
            [0x1A, 0x98, 0x2C, 0x7E, 0x45, 0x9A],
            [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7],
            [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        ]

        # Global config variables
        self.config_key, self.config_key_type = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], self.KeyTypes["A"]

        # Configure logging
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

        # Initialize reader
        self.reader = self.init_reader()
        

    def init_reader(self):
        reader = None

        # Connect to reader
        try:
            reader = nfc.Reader()
            logging.info("Connected to reader..")
        except py122u.error.NoReader:
            logging.error("Error: No reader found.")
            sys.exit(1)

        # Connect to card
        try:
            reader.connect()
            logging.info("Connected to card..")
        except py122u.error.NoCommunication:
            logging.error("Error: No card present.")
            sys.exit(1)
        
        return reader


    def read_uid(self):
        return self.reader.get_uid()
    
    def identify_card(self):
        self.reader.info()
        #print(f"Card Type: {card_info['card_type']}")
        #print(f"UID: {card_info['uid']}")
        #print(f"ATR: {card_info['atr']}")

    def authenticate_block(self, block, key=None, key_type=None):
        # Validate input
        if key_type is None:
            logging.warning("Using default key type.")
            key_type = self.config_key_type
        if key is None:
            logging.warning("Using default key.")
            key = self.config_key

        if key_type not in self.KeyTypes.values():
            raise ValueError("Invalid key type.")
        if len(key) != 6:
            raise ValueError("Invalid key length.")
        if block < 0 or block > 63:
            raise ValueError("Invalid block number.")
        
        # Set key location based on key type
        key_location = self.KeyLocation["A"] if key_type == self.KeyTypes["A"] else self.KeyLocation["B"]

        # Load key
        try:
            self.reader.load_authentication_data(key_location, key)
            logging.info(f"Loaded the key {key} as location {key_location}..")
        except py122u.error.InstructionFailed as e:
            logging.error(f"Failed to load authentication data for key {key} as location {key_location}: {e}")
            return False

        # Authenticate
        try:
            self.reader.authentication(block, key_type, key_location)
            logging.info(f"Authenticated using the key {key} as {key_type} for block {block}.")
        except py122u.error.InstructionFailed as e:
            logging.error(f"Authentication failed for block {block} as {key_type}: {e}")
            return False
        
        return True

    def read_block(self, block, key=None, key_type=None):
        try:
            # authenticate to block
            self.authenticate_block(block, key, key_type)

            # Read block
            data = self.reader.read_binary_blocks(block, 16)
            logging.debug(f"Block {block}: {data}")

            return data
        except py122u.error.InstructionFailed as e:
            logging.error(f"Failed to read block {block}: {e}")
            return []

    def write_block(self, block, data, key=None, key_type=None):
        data = data.upper()
        # Validate data format
        if len(data) != 32 or not all(c in "0123456789ABCDEFabcdef" for c in data):
            raise ValueError("Invalid data format. Data must be a 16-byte hexstring.")

        # Authenticate to block
        self.authenticate_block(block, key, key_type)

        # Write block
        result = self.reader.command(
            "update_binary_blocks", [block, 16, bytes.fromhex(data)]
        )
        logging.debug(f"Write result: {result}")

        # Validate write operation
        written_data = self.read_block(block, key, key_type)
        written_data_str = "".join([f"{byte:02x}" for byte in written_data]).upper()  # Convert to hex string
        if written_data_str == data:
            logging.info(f"Write successful for block {block}.")
        else:
            logging.error(f"Write failed for block {block}.")
            logging.info(f"Expected: {data}")
            logging.info(f"Received: {written_data_str}")

    def read_sector(self, sector):
        blocks = []
        for block in range(sector * 4, (sector + 1) * 4):
            block_data = self.read_block(block)
            blocks.append(block_data)
        return blocks

    def display_sector(self, sector, data_format):
        # Validate input
        if type(sector) != int or sector < 0 or sector > 15:
            raise ValueError("Invalid sector number.")
        
        blocks = self.read_sector(sector)

        # Prepare table data
        table = []
        for i, block_data in enumerate(blocks):
            if data_format == 'hexstring':
                formatted_data = " ".join([f"{byte:02X}" for byte in block_data])
            elif data_format == 'string':
                formatted_data = "".join([chr(byte) if 32 <= byte <= 126 else '.' for byte in block_data])
            elif data_format == 'bytestring':
                formatted_data = block_data
            else:
                raise ValueError("Invalid data format.")
            table.append([f"Block {sector * 4 + i}", formatted_data])

        # Log sector information
        print(f"Displaying sector {sector}")

        # Print blocks as a sector table
        headers = ["Block", "Data"]
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

    def read_full(self, data_format):  
        # Read and collect each sector
        sectors = []
        for sector in range(0, 16):
            blocks = self.read_sector(sector)
            sectors.append({"Sector ID": sector, "Blocks": blocks})

        # Prepare table data
        table = []
        for sector in sectors:
            sector_id = sector["Sector ID"]
            blocks = sector["Blocks"]
            for block_id, block_data in enumerate(blocks):
                block_number = sector_id * 4 + block_id
                if data_format == 'hexstring':
                    formatted_data = " ".join([f"{byte:02X}" for byte in block_data])
                elif data_format == 'string':
                    formatted_data = "".join([chr(byte) if 32 <= byte <= 126 else '.' for byte in block_data])
                elif data_format == 'bytestring':
                    formatted_data = block_data
                else:
                    raise ValueError("Invalid data format.")
                table.append([f"Sector {sector_id}", f"Block {block_number}", formatted_data])

        # Print sectors as a table
        headers = ["Sector ID", "Block ID", "Data"]
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

    # Mifare attacks
    def nested_attack(self):
        # Check if the system is Windows
        if platform.system() == "Windows":
            logging.error("This feature is currently not compatible with Windows and requires the mfoc binary.")
            return

        # Check if mfoc binary is available
        if shutil.which("mfoc"):
            logging.info("mfoc binary found.")
        else:
            logging.error("mfoc binary not found.")
            return
        
        # Create file string with datetime stamp and UID
        uid_hex = ''.join(f"{byte:02X}" for byte in self.read_uid())
        file_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_" + uid_hex + ".mfd"

        # Invoke mfoc to find keys for a Mifare Classic card
        try:
            subprocess.run(["mfoc", "-O", file_string], check=True)
        except FileNotFoundError:
            logging.error("mfoc binary not found.")
            return

    def hardnested_attack(self, key: list, key_type: str, target_block: int, target_key_type: str):
        # Check if the system is Windows
        if platform.system() == "Windows":
            logging.error("This feature is currently not compatible with Windows and requires the libnfc_crypto1_crack binary.")
            return

        # Check if mfoc binary is available
        if shutil.which("libnfc_crypto1_crack"):
            logging.info("libnfc_crypto1_crack binary found.")
        else:
            logging.error("libnfc_crypto1_crack binary not found.")
            return
        
        # Example command ./libnfc_crypto1_crack 000000000000 0 A 4 A
        command = ["libnfc_crypto1_crack", "".join(f"{byte:02X}" for byte in key), str(key_type), str(target_block), str(target_key_type)]
        print(command)
        
    def brute_force(self, key_file, target_block, key_type):
        valid_key = None
        try:
            with open(key_file, 'r') as file:
                total_keys = sum(1 for _ in file)
                file.seek(0)  # Reset file pointer to the beginning
                print(f"Total keys: {total_keys}")
                bar = progressbar.ProgressBar(maxval=total_keys)
                bar.start()
                logging.getLogger().setLevel(logging.CRITICAL) # Disable logging so the progress bar is not spammed
                for i, line in enumerate(file):
                    key = line.strip()
                    # Convert key value to bytes
                    byte_key = [int(key[i:i+2], 16) for i in range(0, len(key), 2)]
                    try:
                        if self.authenticate_block(target_block, key=byte_key, key_type=self.KeyTypes[key_type]):
                            valid_key = key
                            logging.info(f"Valid key found (Type {key_type}): {key}")
                            break
                    except Exception as e:
                        logging.debug(f"Failed to read block with key (Type B): {key}. Error: {str(e)}")
                    bar.update(i + 1)  # Update progress bar
                bar.finish()
        except FileNotFoundError:
            logging.error(f"Key file '{key_file}' not found.")
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Exiting..")
        except Exception as e:
            logging.error(f"Failed to brute force keys: {str(e)}")
        finally:
            logging.getLogger().setLevel(self.args.log_level) # Reset log level

        # Check if a valid key was found
        if valid_key is None:
            logging.info(f"No valid key found (Type {key_type}) for block {target_block}.")
        else:
            logging.info(colored(f"Valid key found (Type {key_type}): {valid_key} for block {target_block}.", "green"))

    # power cycle antenna by sending the apdu command FF00000004D4320100 and FF00000004D4320101
    def power_cycle_antenna(self):
        self.send_apdu_command([0xFF, 0x00, 0x00, 0x00, 0x04, 0xD4, 0x32, 0x01, 0x00])
        time.sleep(5)
        self.send_apdu_command([0xFF, 0x00, 0x00, 0x00, 0x04, 0xD4, 0x32, 0x01, 0x01])

    def send_apdu_command(self, apdu_command: list):
        # Send APDU command
        try:
            apdu_response = self.reader.custom(apdu_command)
            logging.info(f"APDU response: {apdu_response}")
        except py122u.error.InstructionFailed as e:
            logging.error(f"Failed to send APDU command: {e}")

    def mute_sound(self):
        self.reader.buzzer_sound(0) # Mute sound
        print("Muted sound on the reader.")

    def beep_sound(self):
        self.reader.buzzer_sound(1) # Unmute sound
        print("Enabled sound on the reader.")

    def disconnect(self):
        logging.info("Closing reader..")
        self.reader.custom

    def run_cli(self):
        print(f"""
                _____ _____ _____ _____
               / ____|  __ \_   _|  __ \\
              | |    | |__) || | | |  | |
              | |    |  _  / | | | |  | |
              | |____| | \ \_| |_| |__| |
               \_____|_|  \_\_____|_____/
                                          v0.3.0
            """)
        

        parser = argparse.ArgumentParser(description='Interact with Mifare Classic 1K cards.')

        # Generic card details
        parser.add_argument('--read_uid', action='store_true', help='Read the UID of the card.')
        parser.add_argument('--identify', action='store_true', help='Identify the card to the user.')

        # Block operations
        parser.add_argument('--read_block', type=int, help='Read a block from the card.')
        parser.add_argument('--write_block', type=int, help='Write a block to the card.')

        # Data 
        parser.add_argument('--data', type=str, help='Data to write to the block.')
        
        # Bigger operations
        parser.add_argument('--read_sector', type=int, help='Read a sector from the card.')
        parser.add_argument('--read_full', action='store_true', help='Read all 16 sectors from the card.')

        # Key options
        parser.add_argument('--key_type', choices=['A', 'B'], default='A', help='Set the key type (A or B).')
        parser.add_argument('--key_value', type=str, default='ffffffffffff', help='Set the key value. (6 bytes, hexstring)')
        parser.add_argument('--key_list', type=str, help='Set the key list file for brute forcing.')
        parser.add_argument('--target_key_type', choices=['A', 'B'], default='A', help='Set the target key type, only used for hardnested attack (A or B).')

        # Mifare attacks
        parser.add_argument('--brute_force_keys', type=int, help='Specify the block you want to brute force and use --key_list as file containing access keys for brute forcing.')
        parser.add_argument('--nested_attack', action='store_true', help='Execute nested attack')
        parser.add_argument('--hardnested_attack', type=int, help='Execute hardnested attack, as value provide the block you know the key for (requires key_value, key_type, target_block, target_key_type)')
        parser.add_argument('--darkside_attack', action='store_true', help='Execute darkside attack')

        # APDU commands
        parser.add_argument('--apdu_command', type=str, help='Send an APDU command to the NFC device.')

        # Sound options
        parser.add_argument('--mute', action='store_true', help='Mute buzzer on the reader.')
        parser.add_argument('--beep', action='store_true', help='Enable buzzer on the reader.')

        # Data format option
        parser.add_argument('--data_format', choices=['hexstring', 'string', 'bytestring'], default='hexstring', help='Set the format for block data output.')

        parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the log level.')
        
        
        parser.add_argument('--flag', action='store_true', help='Provide the flag.')

        # Examples
        parser.epilog = '''Examples:
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
                '''
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
    
        args = parser.parse_args()
        self.args = args

        # Set log level
        logging.getLogger().setLevel(args.log_level)

        # Convert key value to bytes
        args.key_value = [int(args.key_value[i:i+2], 16) for i in range(0, len(args.key_value), 2)]

        # Set global config variables
        self.config_key = args.key_value
        self.config_key_type = self.KeyTypes[args.key_type]

        # Run the command
        if args.read_uid:
            self.read_uid()
        elif args.identify:
            self.identify_card()
        elif args.read_block is not None:
            data = self.read_block(args.read_block, key=args.key_value, key_type=self.KeyTypes[args.key_type])
            if args.data_format == 'hexstring':
                data_str = " ".join([f"{byte:02X}" for byte in data])
            elif args.data_format == 'string':
                data_str = "".join([chr(byte) if 32 <= byte <= 126 else '.' for byte in data])
            elif args.data_format == 'bytestring':
                data_str = data
            else:
                raise ValueError("Invalid data format.")
            print(f"Block {args.read_block}: {data_str}")
        elif args.write_block is not None and args.data is not None:
            self.write_block(args.write_block, args.data, key=args.key_value, key_type=self.KeyTypes[args.key_type])
        elif args.read_sector is not None:
            self.display_sector(args.read_sector, args.data_format)
        elif args.read_full:
            self.read_full(args.data_format)
        elif args.nested_attack:
            self.nested_attack()
        elif args.hardnested_attack:
            self.hardnested_attack(args.key_value, self.KeyTypes[args.key_type], args.read_block, self.KeyTypes[args.target_key_type])
        elif args.darkside_attack:
            print("Not implemented yet.")
        elif args.apdu_command is not None:
                # Convert hexstring to bytes
                apdu_command = binascii.unhexlify(args.apdu_command)
                self.send_apdu_command(apdu_command)
        elif args.brute_force_keys is not None: 
            # Check if key list file is specified
            if args.key_list is None:
                logging.error("Please specify a key list file using --key_list.")
                return
            
            # Check if key type is specified
            if args.key_type is None:
                logging.error("Please specify a key type using --key_type.")
                return

            # Brute force keys
            self.brute_force(args.key_list, args.brute_force_keys, args.key_type)
        elif args.mute:
            self.mute_sound()
        elif args.beep:
            self.beep_sound()
        elif args.flag:
            print(colored("flag{h3lp_m3nu}", "green"))
        else:
            parser.print_help()

        self.disconnect()


def main():
    client = RFIDClient()
    client.run_cli()

if __name__ == "__main__":
    main()