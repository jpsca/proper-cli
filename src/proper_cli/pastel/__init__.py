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
from .pastel import Pastel


__version__ = "0.2.1"
_PASTEL = Pastel(True)


def colorize(message):
    """
    Formats a message to a colorful string.

    :param message: The message to format.
    :type message: str

    :rtype: str
    """
    with _PASTEL.colorized():
        return _PASTEL.colorize(message)


def with_colors(colorized):
    """
    Enable or disable colors.

    :param decorated: Whether to active colors or not.
    :type decorated: bool

    :rtype: None
    """
    _PASTEL.with_colors(colorized)


def add_style(name, fg=None, bg=None, options=None):
    """
    Adds a new style.

    :param name: The name of the style
    :type name: str

    :param fg: The foreground color
    :type fg: str or None

    :param bg: The background color
    :type bg: str or None

    :param options: The style options
    :type options: list or str or None
    """
    _PASTEL.add_style(name, fg, bg, options)


def remove_style(name):
    """
    Removes a style.

    :param name: The name of the style to remove.
    :type name: str

    :rtype: None
    """
    _PASTEL.remove_style(name)


def pastel(colorized=True):
    """
    Returns a new Pastel instance.

    :rtype: Pastel
    """
    return Pastel(colorized)
