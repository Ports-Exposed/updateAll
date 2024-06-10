#!/usr/bin/env python3
import argparse

def update():
    if config.SIMULATE:
        header = "Simulating Update"
        cmd = "eopkg up -n"
    else:
        header = "Upgrading packages"
        cmd = "eopkg up -y"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    return (1, f"Error upgrading packages: {stderr}") if stderr else (0, "Success")

def check_broken():
    if config.SIMULATE:
        header = "Simulating Broken Pkg Check"
    else:
        header = "Broken Pkg Check"
    stdout, stderr = runCommand("eopkg check", config.VERBOSE, header)
    if stderr:
        return 1, "Failed to run \`eopkg check\`"
    if not (
        broken_packages := [
            line.split()[3] for line in stdout.splitlines() if "Broken" in line
        ]
    ):
        return 0, "Good"
    #rPrint(f"Broken packages: {', '.join(broken_packages)}", "warn")
    cmd = f"sudo eopkg it --reinstall {' '.join(broken_packages)}"
    if config.SIMULATE:
        return 0, "Dry-run"
    #rPrint(f"Executing: {cmd}")
    try:
        runCommand(cmd, config.VERBOSE, header)
        return 0, "Reinstalled"
    except Exception as e:
        return 1, f"Error: {e}; Cmd: {cmd}"

def count():
    header = "Counting packages"
    cmd = "eopkg up -n"
    stdout, stderr = runCommand(cmd, config.VERBOSE, header)
    if stdout:
        if "No packages to upgrade" in stdout:
            return 0, "0"
        lines = stdout.split('\n')
        collect = False
        package_count = 0
        for line in lines:
            if "The following packages will be upgraded:" in line:
                collect = True
                continue
            if "Total size of package(s):" in line:
                break
            if collect:
                packages = line.split()
                package_count += len(packages)

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
