import time

import serial
from mcp.server.fastmcp import FastMCP

from server.schemas import BuildResult, CommandResult, MonitorResult
from server.utils.error_parser import parse_errors
from server.utils.pio_runner import run_pio


def register_pio_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def pio_build(project_path: str) -> dict:
        """Compile firmware for the Pio project at a given path."""
        result = run_pio(["run"], cwd=project_path)
        success = result["returncode"] == 0
        response = BuildResult(
            success=success,
            stdout=result["stdout"],
            stderr=result["stderr"],
            errors=[] if success else parse_errors(result["stderr"]),
        )
        return response.model_dump()

    @mcp.tool()
    def pio_upload(project_path: str, port: str | None = None) -> dict:
        """Flash compiled firware to the connected device."""
        args = ["run", "-t", "upload"]
        if port:
            args += ["--upload-port", port]
        result = run_pio(args, cwd=project_path)
        response = CommandResult(
            success=result["returncode"] == 0,
            stdout=result["stdout"],
            stderr=result["stderr"],
        )
        return response.model_dump()

    @mcp.tool()
    def pio_monitor_serial(
        port: str, baud: int = 115200, duration_ms: int = 5000
    ) -> dict:
        """Read serial output from a connected device for the given duration"""
        try:
            ser = serial.Serial(port=port, baudrate=baud, timeout=1)
            lines: list[str] = []
            deadline = time.monotonic() + duration_ms / 1000
            while time.monotonic() < deadline:
                raw = ser.readline()
                if raw:
                    lines.append(raw.decode("utf-8", errors="replace").rstrip())
            ser.close()
            response = MonitorResult(success=True, output="\n".join(lines))
            return response.model_dump()
        except serial.SerialException as e:
            response = MonitorResult(success=False, output="", error=str(e))
            return response.model_dump()
