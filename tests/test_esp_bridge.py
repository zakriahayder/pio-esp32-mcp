import pytest
import requests

from server.tools.esp_bridge import _call, _connect, _disconnect


@pytest.fixture(autouse=True)
def reset_connection():
    """Reset the global connection state before each test"""
    _disconnect()
    yield
    _disconnect()


@pytest.fixture
def tools_response_data():
    return {
        "tools": [
            {"name": "gpio_write", "description": "Set a digital pin HIGH or LOW"},
            {"name": "gpio_read", "description": "Read a digital pin"},
            {"name": "adc_read", "description": "Read analog value 0-4095"},
            {"name": "pwm_write", "description": "Write PWM 0-255"},
        ]
    }


@pytest.fixture
def successful_call_response():
    return {"success": True, "pin": 2, "value": 1}


class MockResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


@pytest.fixture
def connected(monkeypatch):
    data = {
        "tools": [
            {"name": "gpio_write"},
            {"name": "gpio_read"},
            {"name": "adc_read"},
            {"name": "pwm_write"},
        ]
    }

    def mock_get(*args, **kwargs):
        return MockResponse(data)

    monkeypatch.setattr(requests, "get", mock_get)
    _connect("192.168.1.10", 80)


def test_successful_connection(monkeypatch, tools_response_data):
    def mock_get(url, timeout):
        assert url == "http://192.168.1.10:80/tools"
        assert timeout == 5
        return MockResponse(data=tools_response_data)

    monkeypatch.setattr(requests, "get", mock_get)
    res = _connect("192.168.1.10", 80)
    assert res["success"]
    assert res["available_tools"] == [
        "gpio_write",
        "gpio_read",
        "adc_read",
        "pwm_write",
    ]


def test_connection_timeout(monkeypatch):
    def mock_get(url, timeout):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "get", mock_get)
    res = _connect("192.168.1.10", 80)
    assert res["success"] is False
    assert res["error"] == "Cannot reach 192.168.1.10:80"


def test_successful_call(monkeypatch, successful_call_response, connected):
    def mock_post(url, json, timeout):
        assert url == "http://192.168.1.10:80/call"
        assert timeout == 10
        return MockResponse(data=successful_call_response)

    monkeypatch.setattr(requests, "post", mock_post)
    res = _call("gpio_write", {"pin": 2, "value": 1})
    assert res["success"]
    assert res["result"] == successful_call_response


def test_call_not_connected(monkeypatch, successful_call_response):
    res = _call("gpio_write", {"pin": 2, "value": 1})
    assert res["success"] is False
    assert res["error"] == "Not connected. Call esp_connect first."


def test_call_timeout(monkeypatch, successful_call_response, connected):
    def mock_post(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "post", mock_post)
    res = _call("gpio_write", {"pin": 2, "value": 1})
    assert res["success"] is False
    assert res["error"] == "Timeout calling gpio_write"
