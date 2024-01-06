# main.py
from crid.modules.cli import RFIDClient


def main():
    client = RFIDClient()
    client.run_cli()

if __name__ == "__main__":
    main()