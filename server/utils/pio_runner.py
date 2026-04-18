import subprocess
from server.schemas import PioRunnerOutput

def run_pio(args: list[str], cwd: str | None = None) -> PioRunnerOutput:
    """Runs a pio CLI command

    Args:
        args (list[str]):
        cwd (str | None, optional): Defaults to None.

    Returns:
        dict: {returncode, stdout, stderr}
    """
    result = subprocess.run(["pio"] + args, capture_output=True, text=True, cwd=cwd)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

if __name__ == "__main__":
    # Example usage
    print(run_pio(["--version"]))