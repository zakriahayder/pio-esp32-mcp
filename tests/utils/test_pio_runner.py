import subprocess
from unittest.mock import patch

import pytest

from server.utils.pio_runner import run_pio


@pytest.fixture
def successful_proc():
    return subprocess.CompletedProcess(
        args=["pio", "run"], returncode=0, stdout="Build successful", stderr=""
    )


def test_successful_process(successful_proc):
    with patch("subprocess.run", return_value=successful_proc):
        result = run_pio(["run"])
    
    assert result["returncode"] == 0
    assert result["stdout"] == "Build successful"


def test_correct_call_args(successful_proc):
    with patch("subprocess.run", return_value=successful_proc) as mock_run:
        run_pio(["device", "list"])
    assert mock_run.call_args[0][0] == ["pio", "device", "list"]


def test_kwargs(successful_proc):
    with patch("subprocess.run", return_value=successful_proc) as mock_run:
        run_pio(["run"], cwd="/my/firmware")
    assert mock_run.call_args[1]["cwd"] == "/my/firmware"


def test_pio_not_installed():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = run_pio(["run"])
    assert result["returncode"] == 127
    assert "not found" in result["stderr"].lower()


def test_timeout():
    exc = subprocess.TimeoutExpired(cmd=["pio", "run"], timeout=120)
    exc.stdout = ""
    exc.stderr = ""
    with patch("subprocess.run", side_effect=exc):
        result = run_pio(["run"])
    assert result["returncode"] == 124


def test_stderr_is_returned_on_failure():
    proc = subprocess.CompletedProcess(
        args=["pio", "run"],
        returncode=1,
        stdout="",
        stderr="undefined reference to 'setup'",
    )

    with patch("subprocess.run", return_value=proc):
        result = run_pio(["run"])

    assert result["returncode"] == 1
    assert "undefined reference" in result["stderr"]
