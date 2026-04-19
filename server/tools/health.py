from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP


def register_health_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def health_check() -> dict:
        """Simple liveness check."""
        return {
            "ok": True,
            "server": "embedded-mcp-bridge",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
