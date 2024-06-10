#!/usr/bin/env python3
import argparse

def update():
    if config.SIMULATE:
        header = "Simulating Update"
        cmd = "nix-env --dry-run -u '*'"
    else:
        header = "Upgrading packages"
        cmd = "nix-channel --update && nix-env -u '*'"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    return (1, f"Error upgrading packages: {stderr}") if stderr else (0, "Success")

def check_broken():
    if config.SIMULATE:
        header = "Simulating Broken Pkg Check"
        cmd = "nix-store --verify --check-contents --dry-run"
    else:
        header = "Broken Pkg Check"
        cmd = "nix-store --verify --check-contents"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    if stderr:
        return 1, f"Failed to run \'{cmd}\'"
    if not stdout:
        return 0, "No broken packages detected"
    if not config.SIMULATE:
        broken_packages = [line for line in stdout.splitlines() if 'corruption detected' in line]
        if broken_packages:
            return 1, f"Broken packages found: {', '.join(broken_packages)}"
        else:
            return 0, "No broken packages detected"
    return 0, "Dry-run completed"

def count():
    header = "Counting packages"
    cmd = "nix-env --dry-run -u '*'"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    if stdout:
        if "no new versions" in stdout:
            return 0, "0"
        lines = stdout.split('\n')
        package_count = 0
        for line in lines:
            if line.startswith("upgrading"):
                package_count += 1
        return (0, f"Number of upgradable packages: {package_count}") if config.SIMPLE else (0, package_count)
    elif stderr:
        return (1, f"Error counting upgradable packages: {stderr}") if config.SIMPLE else (1, "Error")

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
