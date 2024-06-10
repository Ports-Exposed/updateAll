#!/usr/bin/env python3
import argparse

def update():
    if config.SIMULATE:
        header = "Simulating Update"
        cmd = "snap refresh --list"
    else:
        header = "Upgrading packages"
        cmd = "snap refresh"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    return (1, f"Error upgrading packages: {stderr}") if stderr else (0, "Success")

def check_broken():
    return 1, "Not Implemented"

def count():
    header = "Counting packages"
    cmd = "snap refresh --list"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    if stderr:
        return (1, f"Error counting upgradable packages: {stderr}")  # Ensure always returning a tuple

    if stdout:
        lines = stdout.strip().split('\n')
        if "All snaps up to date" in stdout:
            return (0, "Number of upgradable packages: 0") if config.SIMPLE else (0, 0)

        # Count the lines that represent actual upgradable packages
        package_count = sum(1 for line in lines if line.strip() and not line.strip().startswith("All snaps up to date"))
        return (0, f"Number of upgradable packages: {package_count}") if config.SIMPLE else (0, package_count)
    else:
        # If stdout is empty and there's no error, interpret as no upgradable packages
        return (0, "Number of upgradable packages: 0") if config.SIMPLE else (0, 0)

if __name__ == "__main__":
    try:
        import os, sys
        sys.path.append("..")
        import config
        #from utils import rPrint
        from utils import runCommand
        sys.path.remove("..")
    except ImportError:
        try:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
            import config
            #from utils import rPrint
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
    #from ..utils import rPrint
    from ..utils import runCommand
