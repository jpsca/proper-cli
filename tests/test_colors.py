import pytest

from proper_cli import colors


def fg(name: str) -> str:
    return colors.FG_COLOR.replace("[COLOR]", colors.COLORS[name])


def ul(name: str) -> str:
    return colors.UNDERLINE_COLOR.replace("[COLOR]", colors.COLORS[name])


@pytest.fixture()
def colorize_on(monkeypatch):
    # `COLORIZE` is read from `$COLORTERM` once at import time, so we flip the
    # module attribute directly to exercise the "terminal supports color" path.
    monkeypatch.setattr(colors, "COLORIZE", "truecolor")


# style() ---------------------------------------------------------------------


def test_style_combines_fg_and_ul():
    out = colors.style(fg="amber-3", ul="green-1")
    assert fg("amber-3") in out
    assert ul("green-1") in out


def test_style_bold_and_dim_are_independent_opt_ins():
    # No weight is applied unless explicitly requested: a plain color is
    # neither bold nor dim.
    plain = colors.style(fg="amber-3")
    assert colors.BOLD not in plain
    assert colors.DIM not in plain

    bold = colors.style(fg="amber-3", bold=True)
    assert colors.BOLD in bold and colors.DIM not in bold

    dim = colors.style(fg="amber-3", dim=True)
    assert colors.DIM in dim and colors.BOLD not in dim


# colorize() ------------------------------------------------------------------


def test_colorize_disabled_strips_all_tags(monkeypatch):
    monkeypatch.setattr(colors, "COLORIZE", None)
    out = colors.colorize("<color fg:red-1 b>hello</color>")
    assert out == "hello"


def test_colorize_tag_without_styles(colorize_on):
    # Regression: style-less tags like `<color fg:amber-3>` are used throughout
    # main.py. They must be colorized, not leaked into the output as literal
    # text while the matching `</color>` gets stripped.
    out = colors.colorize("<color fg:amber-3>Usage:</color>")
    assert "<color" not in out
    assert out.startswith(fg("amber-3"))
    assert "Usage:" in out
    assert out.endswith(colors.RESET)


def test_colorize_tag_with_multiple_attributes(colorize_on):
    # Regression: fg and ul must all apply together (as the docstring
    # documents). The previous regex alternation allowed only one of them.
    out = colors.colorize("<color fg:red-1 ul:green-1 b>x</color>")
    assert fg("red-1") in out
    assert ul("green-1") in out
    assert colors.BOLD in out


def test_colorize_tag_with_only_styles(colorize_on):
    # Each style char maps to its code end-to-end (here `i`->italic, `d`->dim).
    out = colors.colorize("<color id>x</color>")
    assert "<color" not in out
    assert colors.ITALIC in out
    assert colors.DIM in out
    assert out.endswith(f"x{colors.RESET}")
