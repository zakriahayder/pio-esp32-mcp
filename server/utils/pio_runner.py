import subprocess

from server.schemas import PioRunnerOutput


def run_pio(args: list[str], cwd: str | None = None) -> dict:
    """Runs a pio CLI command

    Args:
        args (list[str]):
        cwd (str | None, optional): Defaults to None.

    Returns:
        dict: {returncode, stdout, stderr}
    """
    result = subprocess.run(
        ["pio"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    res = PioRunnerOutput(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
    return res.model_dump()


if __name__ == "__main__":
    # Example usage
    print(run_pio(["--version"]))
