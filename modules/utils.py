#!/usr/bin/env python3
import datetime
import subprocess
import sys
import time
from getpass import getpass
from rich.console import Console; console = Console()
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich import box
try:
    from . import config
except ImportError:
    import config

def runCommand(command, show_output=False, header=None, decoration=None):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = '', ''

    if show_output:
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAVY)
        table.add_column(header, style="dim")
        with Live(table, refresh_per_second=4, console=Console()) as live:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stdout += output
                    if show_output:
                        table.add_row(output.strip())
                        live.update(table)
    else:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                stdout += output
                if show_output:
                    sys.stdout.write(output)
                    sys.stdout.flush()

    stderr = process.communicate()[1]
    if process.returncode != 0:
        sys.stderr.write(stderr)
        sys.stderr.flush()

    return stdout, stderr if process.returncode != 0 else None

def rPrint(message=None, type=None, customStyle=None, tableData=None):
    if customStyle is None:
        customStyle = ""
    match str(type).lower():
        case 'rule':
            console.rule(message, style=customStyle)
            return
        case 'panel':
            pTitle = ""
            pMessage = ""
            if message is not None:
                pTitle = message.get('title')
                pMessage = message.get('message')
            console.print(Panel(pMessage, title=pTitle), style=customStyle)
            return
        case 'table':
            if tableData is not None:
                console.print(tableData, style=customStyle)
            else:
                console.print(message, style=customStyle)
            return
        case 'log':
            console.log(f"{datetime} | {message}", style=customStyle)
            return
        case 'error':
            message = f'❌  {str(message)}'
            customStyle = f'bold red {customStyle} '
        case 'warn':
            message = f'⚠️  {str(message)}'
            customStyle = f'bold yellow {customStyle}'
        case 'info':
            message = f'ℹ️  {str(message)}'
            customStyle = f'bold cyan {customStyle}'
        case 'pop':
            message = str(message)
            customStyle = f'bold magenta {customStyle}'
        case 'success':
            message = f'✅  {str(message)}'
            customStyle = f'bold green {customStyle}'
        case 'getpass':
            message = f'❔  {str(message)} » '
            customStyle = f'bold cyan {customStyle}'
            console.print(f'{message}', style=customStyle, end=""); sys.stdout.flush()
            return getpass(prompt='')
        case 'prompt':
            message = f'❔  {str(message)} » '
            if "skip-input" in customStyle:
                customStyle = customStyle.replace("skip-input", "")
                type = "skip-prompt"
            customStyle = f'bold cyan {customStyle}'
            console.print(f'{message}', style=customStyle, end=""); sys.stdout.flush()
            if type == "skip-prompt":
                return
            return input()
        # case _:
    console.print(message, style=customStyle)
    return