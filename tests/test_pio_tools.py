import pytest

from server.tools import pio_tools
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
    assert result == {
        "ssid": "TestNetwork",
        "password": "testpass123",
        "configured": True,
    }


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


def test_flash_base_firmware_fails_when_platform_ini_missing(tmp_path, set_env):
    firmware_dir = tmp_path / "firmware"
    firmware_dir.mkdir()

    res = _flash_base_firmware("COM3", firmware_dir=firmware_dir)

    assert res["success"] is False
    assert "platformio.ini not found" in res["error"]


def test_flash_base_firmware_when_env_section_missing(tmp_path, set_env):
    firmware_dir = tmp_path / "firmware"
    firmware_dir.mkdir()

    ini_path = firmware_dir / "platformio.ini"
    ini_path.write_text(
        """
        [platformio]
        """.strip()
    )
    res = _flash_base_firmware("COM3", firmware_dir=firmware_dir)

    assert res["success"] is False
    assert "Missing [env:esp32dev]" in res["error"]


def test_flash_base_firmware_when_keys_missing(tmp_path, set_env):
    firmware_dir = tmp_path / "firmware"
    firmware_dir.mkdir()

    ini_path = firmware_dir / "platformio.ini"
    ini_path.write_text(
        """
        [env:esp32dev]
        platform = espressif32
        board = esp32dev
        """.strip()
    )
    res = _flash_base_firmware("COM3", firmware_dir=firmware_dir)
    assert res["success"] is False
    assert "Missing required PlatformIO config values" in res["error"]
    assert "framework" in res["error"]


def test_flash_base_firmware_build_error(tmp_path, set_env, monkeypatch):
    firmware_dir = tmp_path / "firmware"
    firmware_dir.mkdir()

    ini_path = firmware_dir / "platformio.ini"
    ini_path.write_text(
        """
        [env:esp32dev]
        platform = espressif32
        board = esp32dev
        framework = arduino
        """.strip()
    )

    def fake_run_pio(args, cwd=None):
        return {
            "returncode": 1,
            "stdout": "error",
            "stderr": "error",
        }

    monkeypatch.setattr(pio_tools, "run_pio", fake_run_pio)

    res = _flash_base_firmware("COM3", firmware_dir=firmware_dir)
    assert res["success"] is False
    assert res["error"] == "Build failed"
    assert res["stdout"] == "error"
    assert res["stderr"] == "error"
