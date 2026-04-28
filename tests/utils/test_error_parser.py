from server.utils.error_parser import parse_errors


def test_empty_stderr_returns_empty_list():
    assert parse_errors("") == []


def test_single_error_is_parsed():
    stderr = "src/main.cpp:5:5: error: 'foo' was not declared in this scope"
    errors = parse_errors(stderr)
    assert len(errors) == 1
    assert errors[0]["file"] == "src/main.cpp"
    assert errors[0]["line"] == 5
    assert errors[0]["message"] == "'foo' was not declared in this scope"


def test_multiple_errors_are_all_captured():
    stderr = (
        "src/test.cpp:10:5: error: 'foo' was not declared in this scope\n"
        "src/main.cpp:15:3: error: expected ';' before '}' token\n"
    )
    errors = parse_errors(stderr)
    assert len(errors) == 2
    assert errors[1]["line"] == 15


def test_warnings_are_not_included():
    stderr = "src/main.cpp:10:9: warning: unused variable 'x' [-Wunused-variable]"
    assert parse_errors(stderr) == []


def test_successful_build_output_returns_empty_list():
    stderr = (
        "RAM:   [=         ]   6.4% (used 21112 bytes from 327680 bytes)\n"
        "Flash: [==        ]  18.3% (used 239845 bytes from 1310720 bytes)\n"
        "======== [SUCCESS] Took 2.34 seconds ========\n"
    )
    assert parse_errors(stderr) == []
