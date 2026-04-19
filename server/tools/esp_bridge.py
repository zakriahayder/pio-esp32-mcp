from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

_connection: dict | None = None


def _connect(ip: str, port: int = 80) -> dict:
    global _connection
    try:
        resp = requests.get(f"http://{ip}:{port}/tools", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        tools = [t["name"] for t in data.get("tools", [])]
        # Update the global connection variable
        _connection = {"ip": ip, "port": port, "tools": tools}
        return {"success": True, "available_tools": tools}
    except requests.Timeout:
        return {"success": False, "error": f"Cannot reach {ip}:{port}"}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def _call(tool_name: str, args: dict) -> dict:
    global _connection
    if _connection is None:
        return {"success": False, "error": "Not connected. Call esp_connect first."}
    ip, port = _connection["ip"], _connection["port"]
    try:
        resp = requests.post(
            f"http://{ip}:{port}/call",
            json={"tool": tool_name, "args": args},
            timeout=10,
        )
        resp.raise_for_status()
        return {"success": True, "result": resp.json()}
    except requests.Timeout:
        return {"success": False, "error": f"Timeout calling {tool_name}"}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def _disconnect() -> dict:
    global _connection
    _connection = None
    return {"success": True}


def register_esp_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def esp_connect(ip: str, port: int = 80) -> dict:
        """Connect to the ESP32's HTTP tool server.

        Use this only after the board's IP address has been discovered, usually by
        calling pio_list_devices and then pio_monitor_serial to inspect serial logs.
        This tool queries the ESP32 for its available remote tools and stores the
        connection for later esp_call requests.
        """
        return _connect(ip, port)

    @mcp.tool()
    def esp_call(tool_name: str, args: dict[str, Any] | None = None) -> dict:
        """Call a tool exposed by the connected ESP32 over HTTP.

        Use this after esp_connect succeeds. The tool_name should normally come from
        the available_tools returned by esp_connect. This is the final step after
        serial discovery and network connection have already been completed.
        """
        return _call(tool_name, args or {})

    @mcp.tool()
    def esp_disconnect() -> dict:
        """Forget the currently connected ESP32 session.

        Use this when the assistant should explicitly close out the current target
        device before connecting to another ESP32 or ending the workflow.
        """
        return _disconnect()
