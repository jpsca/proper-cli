"""
Copyright (c) 2018 Sébastien Eustace

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys
from contextlib import contextmanager

from proper_cli import pastel


class PseudoTTY(object):
    def __init__(self, underlying):
        self._underlying = underlying

    def __getattr__(self, name):
        return getattr(self._underlying, name)

    def isatty(self):
        return True


@contextmanager
def mock_stdout():
    original = sys.stdout
    sys.stdout = PseudoTTY(sys.stdout)

    yield

    sys.stdout = original


def test_text():
    with mock_stdout():
        assert "\033[32msome info\033[0m" == pastel.colorize("<info>some info</info>")


def test_colorize():
    with mock_stdout():
        pastel.with_colors(False)
        assert "some info" == pastel.colorize("<info>some info</info>")

        pastel.with_colors(True)
        assert "\033[32msome info\033[0m" == pastel.colorize("<info>some info</info>")


def test_add_remove_style():
    with mock_stdout():
        pastel.add_style("success", "green")

        assert "\033[32msome info\033[0m" == pastel.colorize(
            "<success>some info</success>"
        )

        pastel.remove_style("success")

        assert "<success>some info</success>" == pastel.colorize(
            "<success>some info</success>"
        )


def test_pastel():
    p = pastel.pastel()
    assert isinstance(p, pastel.Pastel)
