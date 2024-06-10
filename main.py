#!/usr/bin/env python3
import argparse
import importlib.util
import io
import os
import subprocess
import sys
from modules import config
from modules.utils import rPrint
from rich import box
from rich.console import Console; console = Console()
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.spinner import Spinner
from sys import platform

_NAME = "updateAll"
_AUTHOR = "Leora | Ports.Exposed"
_REPO = "https://github.com/Ports-Exposed/updateAll"

_VERSION = 0.1

CHECK_BROKEN = False

os_pms = {
    "general": ["docker", "pip3", "pip"],
    "FreeBSD": ["freebsd-update:pkgng:pkg"],
    "Linux": {
        "general": ["snap", "flatpak", "nix"],
        "Solus": ["eopkg"],
        "Void": ["xbps-install"], 
        "Bedrock": ["eopkg", "apt-get", "dnf", "yum", "zypper", "pacman", "yay", "emsdk"],
        "Nix": ["nix"],
        "Debian": ["apt-get"],
        "Ubuntu": ["apt-get"],
        "Fedora": ["dnf"],
        "CentOS": ["dnf:yum"],
        "RHEL": ["dnf:yum"],
        "Rocky": ["dnf:yum"],
        "Alma": ["dnf:yum"],
        "Arch": ["pacman:yay"],
        "openSUSE": ["zypper"]
    },
    "AIX": ["aixpkg"],
    "Emscripten": ["emsdk"],
    "WASI": ["emsdk"],
    "Windows": ["choco", "winget"],
    "Cygwin": ["apt-cyg"],
    "Darwin": ["brew"]
}

p2o = {
    'freebsd': 'FreeBSD',
    'linux': 'Linux',
    'aix': 'AIX',
    'emscripten': 'Emscripten',
    'wasi': 'WASI',
    'win32': 'Windows',
    'cygwin': 'Cygwin',
    'darwin': 'Darwin'
}

def osName():
    return next(
        (osN for pltfm, osN in p2o.items() if platform.startswith(pltfm)), None
    )

def parse_args():
    parser = argparse.ArgumentParser(prog=_NAME, description="Universal Package Manager Update Utility")
    
    parser.add_argument('-H', '--full-help', action='store_true', help=f'Display full {_NAME} help')
    parser.add_argument('-v', '--version', action='version', version=f'{_NAME} | {_VERSION}\n{_AUTHOR}\n{_REPO}')

    subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')

    parser_update = subparsers.add_parser('update', aliases=['up'], help='Update packages')
    parser_update.add_argument('-c', '--check-broken', action='store_true', help='Check for broken packages after updating where supported')
    parser_update.add_argument('-p', '--simple', action='store_true', help='Don\'t use Live Table output for Package Manager Status') # Not really accurate I guess. Might need to rename
    parser_update.add_argument('-S', '--simulate', action='store_true', help='Dry run/simulate update process')
    parser_update.add_argument('-s', '--skip', nargs='+', help='Skip specified package managers')  # Not Implemented
    parser_update.add_argument('-V', '--verbose', action='store_true', help='Enable verbose output')
    parser_update.add_argument('package_managers', nargs='*', help='Whitelist of package managers to use')

    parser_count = subparsers.add_parser('count', aliases=['ct'], help='Count upgradable packages')
    parser_count.add_argument('-p', '--simple', action='store_true', help='Don\'t use Live Table output for Package Manager Status')
    parser_count.add_argument('-s', '--skip', nargs='+', help='Skip specified package managers')  # Not Implemented
    parser_count.add_argument('-V', '--verbose', action='store_true', help='Enable verbose output')
    parser_count.add_argument('package_managers', nargs='*', help='Whitelist of package managers to use')

    parser_check_broken = subparsers.add_parser('check-broken', aliases=['ck'], help='Check for broken packages where supported')
    parser_check_broken.add_argument('-p', '--simple', action='store_true', help='Don\'t use Live Table output for Package Manager Status')
    parser_check_broken.add_argument('-S', '--simulate', action='store_true', help='Dry run/simulate check process')
    parser_check_broken.add_argument('-s', '--skip', nargs='+', help='Skip specified package managers')  # Not Implemented
    parser_check_broken.add_argument('-V', '--verbose', action='store_true', help='Enable verbose output')
    parser_check_broken.add_argument('package_managers', nargs='*', help='Whitelist of package managers to use')

    args = parser.parse_args()
    def capture_help(parser):
        s = io.StringIO()
        parser.print_help(file=s)
        return s.getvalue()
    if args.full_help:
        console = Console()
        helpTable = Table(title=f"{_NAME} Help Info", show_header=True, header_style="bold magenta", box=box.ROUNDED)
        helpTable.add_column("Operation", style="dim", no_wrap=True)
        helpTable.add_column("Help", style="dim")

        helpTable.add_row("updateAll", capture_help(parser))

        helpTable.add_row("update", capture_help(parser_update))
        helpTable.add_row("count", capture_help(parser_count))
        helpTable.add_row("check-broken", capture_help(parser_check_broken))
        
        console.print(helpTable)
        sys.exit(0)
    return args

def anyKey():
    try:
        if sys.platform.startswith('win'):
            import msvcrt
            msvcrt.getch()
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except Exception as e:
        input()

# This ones a doozie. Mbad
def managePackages(operation, package_managers):
    if config.VERBOSE or config.SIMPLE:
        failed_pms = []
        success_pms = []
        for pm in package_managers:
            alternatives = pm.split(':')
            for alt in alternatives:
                alt_module_name = alt.replace('-', '_')
                module_name = f'modules.pm.{alt_module_name}'
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                        if func := getattr(module, operation, None):
                            rPrint(f"{alt}", "rule", "bold yellow")
                            # rPrint(f"  ❥ {alt}", None, "bold light_coral")
                            result, msg = func()
                            if result == 0:
                                # rPrint("Operation completed successfully.", "success") if config.VERBOSE else rPrint("", "success")
                                if msg:
                                    print(msg)
                                success_pms.append(alt)
                                break
                            else:
                                failed_pms.append(alt)
                                if config.VERBOSE:
                                    rPrint(f"Error in executing {operation} for {alt} with error code {result}", 'error')
                                    if len(alternatives) > 1 and alt != alternatives[-1]:
                                        rPrint('Trying next alternative...')
                                    # Check if number of items in alternatives is greater than 1
                                    elif len(alternatives) > 1 and alt == alternatives[-1]:
                                        rPrint(f"All alternatives failed for {pm}.", 'info')
                                else:
                                    rPrint(f"{alt} failed", 'error')

                    except Exception as e:
                        failed_pms.append(alt)
                        if config.VERBOSE:
                            rPrint(f"Error while executing {operation} for {alt}: {e}", 'error')
                            if len(alternatives) > 1 and alt == alternatives[-1]:
                                rPrint(f"All alternatives failed for {pm}. 2", 'info')
                        else:
                            rPrint(f"{alt} | {e}", 'error')
                else:
                    failed_pms.append(alt)
                    rPrint(f"Module for {alt} not found.", 'error')
                    if config.VERBOSE and alt == alternatives[-1]:
                        rPrint(f"All alternatives failed for {pm}.", 'info')
        if failed_pms:
            rPrint("Summary", "rule", "yellow") if config.VERBOSE else rPrint("Issues", "rule", "yellow")
            rPrint(f"Failed: {', '.join(failed_pms)}", 'error')
            if config.VERBOSE and success_pms:
                rPrint(f"Success: {', '.join(success_pms)}", 'success')
    else:
        opName = operation[0].upper() + operation[1:]
        if config.SIMULATE:
            opName = f"Simulated {opName}"
        status_table = Table(title=opName, show_header=True, header_style="bold blue", box=box.MINIMAL_HEAVY_HEAD)
        status_table.add_column("Package Manager", style="dim")
        if operation == 'update':
            status_table.add_column("Status", justify="right")
        elif operation == 'check-broken':
            status_table.add_column("Broken", justify="right")
        elif operation == 'count':
            status_table.add_column("Count", justify="right")

        output_table = Table(title="Details and Outputs", show_header=True, header_style="bold green", box=box.SIMPLE_HEAD)
        output_table.add_column("Output", style="dim")

        #footer = Table(show_header=False, box=box.SIMPLE_HEAD)
        #footer.add_row("Press any key to exit")
        footer = Layout()
        spinner = Spinner("dots", text="Running...", style="bold green")
        footer.update(spinner)
        #footer.add_row("Press any key to exit")

        layout = Layout()  # Creating a layout
        terminalWidth = os.get_terminal_size().columns
        terminalHeight = os.get_terminal_size().lines
        pms = []
        for pm in package_managers:
            pms.append(pm.split(':'))
        minW = len(pms) + 5
        minH = (len(pms) * 2) + 16
        if terminalWidth < 100:
            if terminalHeight < minH or terminalWidth < 40:
                config.SIMPLE = True
                managePackages(operation, package_managers)
                return
            else:
                layout.split_column(
                    Layout(status_table, name='status', minimum_size=minW, ratio=1),
                    Layout(output_table, name='output', ratio=62),
                    Layout(footer, name='footer', minimum_size=4)
                )
        elif terminalHeight > (minH / 2 + 2):
            layout.split(
                Layout(name='main', ratio=95),
                Layout(name='footer', ratio=5, minimum_size=4)
            )
            layout['main'].split_row(
                Layout(status_table, name='status', minimum_size=40, ratio=1),
                Layout(output_table, name='output', ratio=62)
            )
            layout['footer'].update(footer)
        else:
            config.SIMPLE = True
            managePackages(operation, package_managers)
            return
        #layout["footer"].visible = False

        layout["output"].visible = False
        with Live(layout, console=console, refresh_per_second=10, screen=True) as live:
            for pm in package_managers:
                alternatives = pm.split(':')
                pm_status = "Failed"
                for alt in alternatives:
                    alt_module_name = alt.replace('-', '_')
                    module_name = f'modules.pm.{alt_module_name}'
                    spec = importlib.util.find_spec(module_name)
                    if spec is not None:
                        module = importlib.util.module_from_spec(spec)
                        try:
                            spec.loader.exec_module(module)
                            if func := getattr(module, operation, None):
                                func_result = func()
                                if isinstance(func_result, tuple):
                                    result, msg = func_result
                                else:
                                    result = func_result
                                    msg = "No detailed output available"

                                if result == 0:
                                    if msg:
                                        pm_status = msg
                                    else:
                                        pm_status = "Success"
                                    break
                                else:
                                    layout["output"].visible = True
                                    output_table.add_row(f"{alt} Error: {msg}")
                            else:
                                layout["output"].visible = True
                                output_table.add_row(f"{alt} has no {operation} operation.")
                        except Exception as e:
                            layout["output"].visible = True
                            output_table.add_row(f"{alt} Exception: {str(e)}")
                    else:
                        layout["output"].visible = True
                        output_table.add_row(f"{alt} module not found.")
                status_table.add_row(pm, str(pm_status))
                live.refresh()
            #layout["footer"].visible = True
            layout['footer'].update(Layout("Press any key to exit"))
            anyKey()


def adminCheck():
    try:
        if config.OS != "Windows":
            return os.geteuid() == 0
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False

def main():
    args = parse_args()
    if hasattr(args, 'simple'):
        config.SIMPLE = args.simple
    if hasattr(args, 'simulate'):
        config.SIMULATE = args.simulate
    if hasattr(args, 'verbose'):
        config.VERBOSE = args.verbose
    if config.OS is None:
        config.OS = osName()
    if not adminCheck():
        if config.OS == "Windows":
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            print(f"{_NAME} requires superuser access. Please re-run with sudo or as root.")
            exit(1)
    if config.VERBOSE:
        rPrint(f"OS is {config.OS}")

    if config.OS:
        applicable_pms = os_pms.get("general", [])

        if config.OS == 'Linux':
            applicable_pms.extend(os_pms['Linux'].get('general', []))
            if config.DISTRO is None:
                config.DISTRO = subprocess.check_output(['lsb_release', '-i', '-s']).decode().strip()
            if config.VERBOSE:
                rPrint(f"Distro is {config.DISTRO}")
            try:
                distro_specific_pms = os_pms['Linux'].get(config.DISTRO, [])
                applicable_pms.extend(distro_specific_pms)
            except KeyError:
                rPrint(f"Distro {config.DISTRO} not found.", 'error')
                exit(1)

        operation = args.operation.replace('-', '_')
        if operation == 'up':
            operation = 'update'
        elif operation == 'ck':
            operation = 'check_broken'
        elif operation == 'ct':
            operation = 'count'
        if hasattr(args, 'check-broken'):
            print("Check broken packages:", args.check_broken)
            input()
        if not applicable_pms:
            rPrint("No applicable package managers found.", 'error')
            exit(1)
        managePackages(operation, applicable_pms)

if __name__ == '__main__':
    main()