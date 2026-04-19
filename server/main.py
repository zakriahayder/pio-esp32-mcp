import logging
import sys

from mcp.server.fastmcp import FastMCP

from server.tools.esp_bridge import register_esp_tools
from server.tools.health import register_health_tools
from server.tools.pio_tools import register_pio_tools

logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

mcp = FastMCP(
    "pio-esp32-mcp",
    instructions=(
        "This server helps an AI assistant build, flash, and communicate with an ESP32 over serial and HTTP. "
        "When asked to create a new PlatformIO project or platformio.ini, call pio_init instead of writing platformio.ini manually. "
        "When the ESP32 IP address is needed, do not ask the user for it first. "
        "First call pio_list_devices to find the serial port, then call pio_monitor_serial on that port "
        "at 115200 baud for a few seconds to read boot or status logs and extract the IP address. "
        "If no IP address appears, build and upload the firmware with pio_build and pio_upload, then monitor serial again. "
        "Use esp_connect only after an IP address has been discovered from serial output."
    ),
    log_level="ERROR",
)
register_pio_tools(mcp)
register_esp_tools(mcp)
register_health_tools(mcp)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
