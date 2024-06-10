#!/usr/bin/env python3
import argparse

def update():
    print("Updating package lists...")
    stdout, stderr = runCommand("sudo apt-get update")
    if stderr:
        return 1, f"Error updating package lists: {stderr}"
    
    print("Upgrading packages...")
    stdout, stderr = runCommand("sudo apt-get upgrade -y")
    if stderr:
        return 1, f"Error upgrading packages: {stderr}"

    print("Update complete.")
    return 0

def count():
    print("Counting upgradable packages...")
    stdout, stderr = runCommand("apt list --upgradable")
    if stderr:
        return 1, f"Error counting upgradable packages: {stderr}"

    upgradable_packages = stdout.splitlines()
    count = len([line for line in upgradable_packages if line and "upgradable" in line]) - 1
    return 0, f"Number of upgradable packages: {count}"

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