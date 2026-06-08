import re

import pytest


@pytest.fixture()
def get_out_text(capsys):
    def out_text():
        out = capsys.readouterr().out
        out = strip_non_visible(out)
        print(out)
        return out

    return out_text


# Any ANSI SGR sequence: `\x1b[`, an optional `;`-separated numeric payload,
# then `m`. Covers the 256-color codes emitted by `colors.py`
# (`\x1b[38;5;214m`, `\x1b[48;5;153m`, `\x1b[4;58;5;151m`) plus the style and
# reset codes, regardless of `$COLORTERM`.
ANSI_SGR = re.compile(r"\x1b\[[0-9;]*m")


def strip_non_visible(text):
    text = ANSI_SGR.sub("", text)
    text = re.sub(r"[ ]+\n", r"\n", text)
    return text
