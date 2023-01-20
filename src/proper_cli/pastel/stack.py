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
from .style import Style


class StyleStack(object):
    def __init__(self, empty_style=None):
        self.empty_style = empty_style or Style()
        self.reset()

    def reset(self):
        self.styles = list()

    def push(self, style):
        self.styles.append(style)

    def pop(self, style=None):
        if not len(self.styles):
            return self.empty_style

        if not style:
            return self.styles.pop()

        for i, stacked_style in enumerate(reversed(self.styles)):
            if style == stacked_style:
                self.styles = self.styles[: len(self.styles) - 1 - i]

                return stacked_style

        raise ValueError("Incorrectly nested style tag found.")

    def get_current(self):
        if not len(self.styles):
            return self.empty_style

        return self.styles[-1]
