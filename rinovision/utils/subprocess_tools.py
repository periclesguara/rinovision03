import shutil
import subprocess


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(args: list[str], timeout: int = 30) -> dict:
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except Exception as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
