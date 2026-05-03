import pytest

from server.tools.pio_tools import _flash_base_firmware, _get_wifi_credentials


@pytest.fixture
def set_env(monkeypatch):
    monkeypatch.setenv("WIFI_SSID", "TestNetwork")
    monkeypatch.setenv("WIFI_PASSWORD", "testpass123")


@pytest.fixture
def del_env(monkeypatch):
    monkeypatch.delenv("WIFI_SSID", raising=False)
    monkeypatch.delenv("WIFI_PASSWORD", raising=False)


def test_get_wifi_credentials_configured(set_env):
    result = _get_wifi_credentials()
    assert result["ssid"] == "TestNetwork"
    assert result["password"] == "testpass123"


def test_get_wifi_credentials_not_configured(del_env):
    result = _get_wifi_credentials()

    assert result == {
        "ssid": "",
        "password": "",
        "configured": False,
    }

def test_flash_base_firmware_fails_without_wifi_ssid(del_env):
    result = _flash_base_firmware("COM3")

    assert result["success"] is False
    assert "WIFI_SSID is not set" in result["error"]
    assert ".mcp.json" in result["error"]