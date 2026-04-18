from server.utils.error_parser import parse_errors


def test_parse_single_error():
    stderr = "src/main.cpp:5:5: error: 'foo' was not declared in this scope"
    errors = parse_errors(stderr)
    assert len(errors) == 1
    assert errors[0] == {
        "file": "src/main.cpp",
        "line": 5,
        "message": "'foo' was not declared in this scope",
    }


def test_parse_multiple_errors():
    stderr = (
        "src/test.cpp:10:5: error: 'foo' was not declared in this scope\n"
        "src/main.cpp:15:3: error: expected ';' before '}' token\n"
    )
    errors = parse_errors(stderr)
    assert len(errors) == 2
    assert errors[0]["file"] == "src/test.cpp"
    assert errors[1]["line"] == 15
    assert errors[1]["message"] == "expected ';' before '}' token"


def test_no_errors():
    stderr = (
        "RAM:   [=         ]   6.4% (used 21112 bytes from 327680 bytes)\n"
        "Flash: [==        ]  18.3% (used 239845 bytes from 1310720 bytes)\n"
        "========================================================================= "
        "[SUCCESS] Took 2.34 seconds "
        "========================================================================="
    )
    assert parse_errors(stderr) == []


def test_non_error():
    stderr = (
        "src/main.cpp: In function 'void loop()':\n"
        "src/main.cpp:10:9: warning: unused variable 'x' [-Wunused-variable]\n"
        "     int x = 0;\n"
        "         ^"
    )
    assert parse_errors(stderr) == []


def test_empty_stderr():
    stderr = ""
    assert parse_errors(stderr) == []
