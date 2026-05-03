import os
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
    try:
        result = subprocess.run(
            ["pio"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            timeout=120,
            env=os.environ.copy(),
        )
        res = PioRunnerOutput(
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
        return res.model_dump()
    except FileNotFoundError:
        return PioRunnerOutput(
            returncode=127,
            stdout="",
            stderr="PlatformIO CLI not found on PATH. Install PlatformIO Core and make sure `pio` is available.",
        ).model_dump()
    except subprocess.TimeoutExpired as exc:
        return PioRunnerOutput(
            returncode=124,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + "\nPlatformIO command timed out after 120 seconds.",
        ).model_dump()

