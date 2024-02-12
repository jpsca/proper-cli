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
import pytest
from proper_cli.pastel.style import Style


def test_push(stack):
    s1 = Style("white", "black")
    s2 = Style("yellow", "blue")
    stack.push(s1)
    stack.push(s2)

    assert s2 == stack.get_current()

    s3 = Style("green", "red")
    stack.push(s3)

    assert s3 == stack.get_current()


def test_pop(stack):
    s1 = Style("white", "black")
    s2 = Style("yellow", "blue")
    stack.push(s1)
    stack.push(s2)

    assert s2 == stack.pop()
    assert s1 == stack.pop()


def test_pop_empty(stack):
    assert isinstance(stack.pop(), Style)


def test_pop_not_last(stack):
    s1 = Style("white", "black")
    s2 = Style("yellow", "blue")
    s3 = Style("green", "red")
    stack.push(s1)
    stack.push(s2)
    stack.push(s3)

    assert s2 == stack.pop(s2)
    assert s1 == stack.pop()


def test_invalid_pop(stack):
    s1 = Style("white", "black")
    s2 = Style("yellow", "blue")
    stack.push(s1)

    with pytest.raises(ValueError):
        stack.pop(s2)
