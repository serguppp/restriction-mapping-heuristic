import subprocess
from pathlib import Path


class CppRunner:
    def __init__(self, exe_path: Path) -> None:
        self.exe_path = exe_path

    def run_generate_p_and_d(self, args: list[str]) -> str:
        process = subprocess.run(
            [self.exe_path, "0", *args], capture_output=True, text=True, check=True
        )

        return process.stdout

    def run_generate_d(self, args: list[str]) -> str:
        process = subprocess.run(
            [self.exe_path, "1", *args], capture_output=True, text=True, check=True
        )
        return process.stdout

    def run_heuristics(self, args: list[str]) -> subprocess.Popen:
        return subprocess.Popen(
            [self.exe_path, "2", *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
