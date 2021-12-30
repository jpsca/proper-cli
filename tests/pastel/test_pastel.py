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


def test_empty_tag(pastel):
    assert "foo<>bar" == pastel.colorize("foo<>bar")


def test_lg_char_escaping(pastel):
    assert "foo<bar" == pastel.colorize("foo\\<bar")
    assert "<info>some info</info>" == pastel.colorize("\\<info>some info\\</info>")
    assert "\\<info>some info\\</info>" == pastel.escape("<info>some info</info>")


def test_bundled_styles(pastel):
    assert pastel.has_style("error")
    assert pastel.has_style("info")
    assert pastel.has_style("comment")
    assert pastel.has_style("question")

    assert "\033[97;41msome error\033[0m" == pastel.colorize(
        "<error>some error</error>"
    )
    assert "\033[32msome info\033[0m" == pastel.colorize("<info>some info</info>")
    assert "\033[33msome comment\033[0m" == pastel.colorize(
        "<comment>some comment</comment>"
    )
    assert "\033[30;46msome question\033[0m" == pastel.colorize(
        "<question>some question</question>"
    )


def test_nested_styles(pastel):
    assert (
        "\033[97;41msome \033[0m\033[32msome info\033[0m\033[97;41m error\033[0m"
        == pastel.colorize("<error>some <info>some info</info> error</error>")
    )


def test_adjacent_style(pastel):
    assert "\033[97;41msome error\033[0m\033[32msome info\033[0m" == pastel.colorize(
        "<error>some error</error><info>some info</info>"
    )


def test_style_matching_non_greedy(pastel):
    assert "(\033[32m>=2.0,<2.3\033[0m)" == pastel.colorize("(<info>>=2.0,<2.3</info>)")


def test_style_escaping(pastel):
    assert "(\033[32mz>=2.0,<a2.3\033[0m)" == pastel.colorize(
        "(<info>%s</info>)" % pastel.escape("z>=2.0,<a2.3")
    )


def test_deep_nested_style(pastel):
    src = "<error>error<info>info<comment>comment</comment></info>error</error>"
    result = pastel.colorize(src)
    expected = (
        "\033[97;41merror\033[0m\033[32minfo\033[0m\033[33mcomment\033"
        "[0m\033[97;41merror\033[0m"
    )
    assert result == expected


def test_new_style(pastel):
    pastel.add_style("test", "blue", "white")

    assert pastel.style("test") != pastel.style("info")

    pastel.add_style("b", "blue", "white")

    assert (
        "\033[34;107msome \033[0m\033[34;107mcustom\033[0m\033[34;107m msg\033[0m"
        == pastel.colorize("<test>some <b>custom</b> msg</test>")
    )

    pastel.remove_style("test")
    pastel.remove_style("b")

    assert "<test>some <b>custom</b> msg</test>" == pastel.colorize(
        "<test>some <b>custom</b> msg</test>"
    )

    with pytest.raises(ValueError):
        pastel.remove_style("b")


def test_redefined_style(pastel):
    pastel.add_style("info", "blue", "white")

    assert "\033[34;107msome custom msg\033[0m" == pastel.colorize(
        "<info>some custom msg</info>"
    )


def test_inline_style(pastel):
    assert "\033[34;41msome text\033[0m" == pastel.colorize(
        "<fg=blue;bg=red>some text</>"
    )
    assert "\033[34;41msome text\033[0m" == pastel.colorize(
        "<fg=blue;bg=red>some text</fg=blue;bg=red>"
    )
    assert "\033[34;41;1msome text\033[0m" == pastel.colorize(
        "<fg=blue;bg=red;options=bold>some text</>"
    )


def test_non_style_tag(pastel):
    expected = (
        "\033[32msome \033[0m\033[32m<tag>\033[0m\033[32m \033[0m\033[32m"
        "<setting=value>\033[0m\033[32m styled \033[0m\033[32m<p>\033"
        "[0m\033[32msingle-char tag\033[0m\033[32m</p>\033[0m"
    )

    assert expected == pastel.colorize(
        "<info>some <tag> <setting=value> styled <p>single-char tag</p></info>"
    )


def test_non_decorated_pastel(non_decorated_pastel):
    pastel = non_decorated_pastel

    assert pastel.has_style("error")
    assert pastel.has_style("info")
    assert pastel.has_style("comment")
    assert pastel.has_style("question")

    assert "some error" == pastel.colorize("<error>some error</error>")
    assert "some info" == pastel.colorize("<info>some info</info>")
    assert "some comment" == pastel.colorize("<comment>some comment</comment>")
    assert "some question" == pastel.colorize("<question>some question</question>")

    pastel.with_colors(True)

    assert "\033[97;41msome error\033[0m" == pastel.colorize(
        "<error>some error</error>"
    )
    assert "\033[32msome info\033[0m" == pastel.colorize("<info>some info</info>")
    assert "\033[33msome comment\033[0m" == pastel.colorize(
        "<comment>some comment</comment>"
    )
    assert "\033[30;46msome question\033[0m" == pastel.colorize(
        "<question>some question</question>"
    )


@pytest.mark.parametrize(
    "expected, message",
    [
        (
            "\033[32m\nsome text\033[0m",
            "<info>\nsome text</info>",
        ),
        (
            "\033[32msome text\n\033[0m",
            "<info>some text\n</info>",
        ),
        (
            "\033[32m\nsome text\n\033[0m",
            "<info>\nsome text\n</info>",
        ),
        (
            "\033[32m\nsome text\nmore text\n\033[0m",
            "<info>\nsome text\nmore text\n</info>",
        ),
    ],
)
def test_content_with_line_breaks(pastel, expected, message):
    assert expected == pastel.colorize(message)
