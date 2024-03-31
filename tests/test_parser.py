from proper_cli.parser import parse_args


def test_parse_args():
    result = parse_args([
        "abc",
        "xy",
        "meh:lorem=ipsum",
        "-w=3",
        "--foo",
        "bar",
        "-narf=zort",
        "qwer=ty"
    ])
    expected = (
        ["abc", "xy", "meh:lorem=ipsum"],
        {"foo": "bar", "w": "3", "narf": ["zort", "qwer=ty"]},
    )
    print(result)
    assert result == expected


def test_parse_args_list():
    result = parse_args(["-f", "1", "-f", "2", "-f", "3"])
    expected = ([], {"f": ["1", "2", "3"]})
    assert result == expected

    result = parse_args(["-f", "1", "2", "3"])
    assert result == expected


def test_parse_args_text():
    result = parse_args(["-foo", "yes, indeed", "-bar", "no"])
    expected = ([], {"foo": "yes, indeed", "bar": "no"})
    assert result == expected


def test_single_flags():
    result = parse_args(["-abc", "-no-cde"])
    expected = ([], {"abc": True, "cde": False})
    assert result == expected


def test_key_n_flag():
    result = parse_args(["-foo", "bar", "-abc"])
    expected = ([], {"abc": True, "foo": "bar"})
    assert result == expected

    result = parse_args(["-abc", "-foo", "bar"])
    assert result == expected


def test_pos_n_flag():
    result = parse_args(["foo", "-abc"])
    expected = (["foo"], {"abc": True})
    assert result == expected


def test_typo_flag():
    result = parse_args(["-abc", "123", "-abc"])
    expected = ([], {"abc": "123"})
    assert result == expected

    result = parse_args(["-abc", "-abc", "123"])
    expected = ([], {"abc": "123"})
    assert result == expected
