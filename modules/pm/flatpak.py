#!/usr/bin/env python3
import argparse

def update():
    if config.SIMULATE:
        header = "Simulating Flatpak Update"
        cmd = "flatpak remote-ls --updates"
    else:
        header = "Updating Flatpak packages"
        cmd = "flatpak update -y"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    return (1, f"Error updating Flatpak packages: {stderr}") if stderr else (0, "Success")

def check_broken():
    # Flatpak doesn't have check for broken functionality.
    return 1, "Checking broken packages is not supported by Flatpak through this tool."

def count():
    header = "Counting upgradable Flatpak packages"
    stdout, stderr = runCommand("flatpak remote-ls --updates", config.VERBOSE, header)
    if stderr:
        return 1, f"Error counting upgradable Flatpak packages: {stderr}"
    upgradable_packages = stdout.splitlines()
    count = len(upgradable_packages)
    return (0, f"Number of upgradable packages: {count}") if config.SIMPLE else (0, count)

if __name__ == "__main__":
    try:
        import os, sys
        sys.path.append("..")
        import config
        from utils import rPrint
        from utils import runCommand
        sys.path.remove("..")
    except ImportError:
        try:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
            import config
            from utils import rPrint
            from utils import runCommand
            sys.path.remove(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
        except ImportError:
            print("Could not import config or utils for test run.")
            exit(1)
    def parse_args():
        parser = argparse.ArgumentParser(description=f"{os.path.basename(__file__)[:-3]} module")
        parser.add_argument('operation', choices=['update', 'count'], help='Operation to perform')
        return parser.parse_args()
    args = parse_args()
    operation = args.operation
    if operation == 'update':
        print("\nTesting update function")
        update()
    elif operation == 'count':
        print("\nTesting count function")
        count()
else:
    from .. import config
    from ..utils import rPrint
    from ..utils import runCommand
