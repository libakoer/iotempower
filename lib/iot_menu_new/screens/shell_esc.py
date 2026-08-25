import os
import platform
import shutil
import subprocess
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button


class ShellScreen(Screen):
    def __init__(self, current_path: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.current_path = Path(current_path or Path.cwd())

    def compose(self) -> ComposeResult:
        yield Button("Open Shell", id="open_shell")
        yield Button("Go back", id="pop")

    def open_shell(self) -> None:
        """Open a terminal in self.current_path."""

        system = platform.system()
        working_directory = self.current_path.expanduser().resolve()

        try:
            if not working_directory.is_dir():
                self.notify(f"Directory does not exist: {working_directory}")
                return

            if system == "Windows":
                # Prefer Windows Terminal
                try:
                    subprocess.Popen(
                        ["wt.exe", "-d", str(working_directory)],
                        cwd=str(working_directory),
                    )
                    return
                except FileNotFoundError:
                    pass

                # Fallback to Command Prompt
                subprocess.Popen(
                    ["cmd.exe", "/K"],
                    cwd=str(working_directory),
                )

            elif system == "Linux":
                # In WSL, the Windows Terminal may ignore the Linux process cwd.
                # Start a WSL tab with the directory passed explicitly instead.
                if os.environ.get("WSL_INTEROP") and shutil.which("wt.exe"):
                    subprocess.Popen(
                        ["wt.exe", "wsl.exe", "--cd", str(working_directory)],
                        cwd=str(working_directory),
                    )
                    return

                terminal_commands = (
                    ("gnome-terminal", ["gnome-terminal", "--working-directory", str(working_directory)]),
                    ("konsole", ["konsole", "--workdir", str(working_directory)]),
                    ("xfce4-terminal", ["xfce4-terminal", "--working-directory", str(working_directory)]),
                    ("mate-terminal", ["mate-terminal", "--working-directory", str(working_directory)]),
                    ("x-terminal-emulator", ["x-terminal-emulator"]),
                    ("tilix", ["tilix", "--working-directory", str(working_directory)]),
                    ("kitty", ["kitty"]),
                    ("alacritty", ["alacritty"]),
                    ("xterm", ["xterm"]),
                )

                for terminal, command in terminal_commands:
                    if shutil.which(terminal):
                        subprocess.Popen(command, cwd=str(working_directory))
                        return

                if shutil.which("bash"):
                    subprocess.Popen(
                        ["bash"],
                        cwd=str(working_directory),
                    )
                    return

                self.notify("No terminal emulator found.")

            elif system == "Darwin":
                subprocess.Popen(
                    [
                        "open",
                        "-a",
                        "Terminal",
                        str(self.current_path),
                    ]
                )

            else:
                self.notify(f"Unsupported platform: {system}")

        except Exception as e:
            self.notify(f"Failed to open terminal: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open_shell":
            self.open_shell()
            event.stop()

        elif event.button.id == "pop":
            self.app.pop_screen()
            event.stop()
