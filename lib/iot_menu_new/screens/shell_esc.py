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
        """Open a new terminal window in the selected directory."""

        try:
            working_directory = self.current_path.expanduser().resolve()

            if not working_directory.is_dir():
                self.notify(f"Directory does not exist: {working_directory}")
                return

            system = platform.system()

            # Windows
            if system == "Windows":
                try:
                    subprocess.Popen(
                        ["wt.exe", "-d", str(working_directory)],
                        cwd=str(working_directory),
                        start_new_session=True,
                    )
                    return
                except FileNotFoundError:
                    pass

                subprocess.Popen(
                    ["cmd.exe", "/K"],
                    cwd=str(working_directory),
                    start_new_session=True,
                )
                return

            # Linux
            elif system == "Linux":

                # WSL support
                if os.environ.get("WSL_INTEROP"):
                    try:
                        subprocess.Popen(
                            [
                                "wt.exe",
                                "wsl.exe",
                                "--cd",
                                str(working_directory),
                            ],
                            start_new_session=True,
                        )
                        return
                    except Exception:
                        pass

                # Ubuntu 25+ default terminal
                if shutil.which("ptyxis"):
                    subprocess.Popen(
                        [
                            "ptyxis",
                            "--new-window",
                        ],
                        cwd=str(working_directory),
                        start_new_session=True,
                    )
                    return

                if shutil.which("gnome-terminal"):
                    subprocess.Popen(
                        [
                            "gnome-terminal",
                            "--working-directory",
                            str(working_directory),
                        ],
                        start_new_session=True,
                    )
                    return

                if shutil.which("konsole"):
                    subprocess.Popen(
                        [
                            "konsole",
                            "--workdir",
                            str(working_directory),
                        ],
                        start_new_session=True,
                    )
                    return

                if shutil.which("xfce4-terminal"):
                    subprocess.Popen(
                        [
                            "xfce4-terminal",
                            "--working-directory",
                            str(working_directory),
                        ],
                        start_new_session=True,
                    )
                    return

                if shutil.which("mate-terminal"):
                    subprocess.Popen(
                        [
                            "mate-terminal",
                            "--working-directory",
                            str(working_directory),
                        ],
                        start_new_session=True,
                    )
                    return

                if shutil.which("tilix"):
                    subprocess.Popen(
                        [
                            "tilix",
                            "--working-directory",
                            str(working_directory),
                        ],
                        start_new_session=True,
                    )
                    return

                if shutil.which("xterm"):
                    subprocess.Popen(
                        ["xterm"],
                        cwd=str(working_directory),
                        start_new_session=True,
                    )
                    return

                self.notify("No terminal emulator found.")
                return

            # macOS
            elif system == "Darwin":
                subprocess.Popen(
                    [
                        "open",
                        "-a",
                        "Terminal",
                        str(working_directory),
                    ],
                    start_new_session=True,
                )
                return

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