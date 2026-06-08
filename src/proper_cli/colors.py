import os
import re


# Values of 256 colors.
COLORS: dict[str, str] = {
    "amber-1": "222",    #ffd787
    "amber-2": "221",    #ffd75f
    "amber-3": "214",    #ffaf00

    "blue-1": "153",     #afd7ff
    "blue-2": "110",     #87afd7
    "blue-3": "33",      #0087ff
    "blue-4": "21",      #0000ff

    "cyan-1": "152",     #afd7d7
    "cyan-2": "123",     #87ffff
    "cyan-3": "45",      #00d7ff
    "cyan-4": "31",      #0087af

    "emerald-1": "122",  #87ffd7
    "emerald-2": "43",   #00d7af
    "emerald-3": "71",   #5faf5f
    "emerald-4": "29",   #00875f

    "fuchsia-1": "225",  #ffd7ff
    "fuchsia-2": "219",  #ffafff
    "fuchsia-3": "13",   #ff54ff
    "fuchsia-4": "165",  #d700ff
    "fuchsia-5": "126",  #af0087

    "green-1": "114",    #87d787
    "green-2": "84",     #5fff87
    "green-3": "35",     #00af5f
    "green-4": "22",     #005f00

    "indigo-1": "147",   #afafff
    "indigo-2": "104",   #8787d7
    "indigo-3": "63",    #5f5fff
    "indigo-4": "4",     #1818b2

    "lime-1": "150",     #afd787
    "lime-2": "10",      #54ff54
    "lime-3": "112",     #87d700
    "lime-4": "100",     #878700

    "orange-1": "223",   #ffd7af
    "orange-2": "173",   #d7875f
    "orange-3": "208",   #ff8700
    "orange-4": "166",   #d75f00

    "pink-1": "182",     #d7afd7
    "pink-2": "175",     #d787af
    "pink-3": "168",     #d75f87
    "pink-4": "161",     #d7005f

    "purple-1": "183",   #d7afff
    "purple-2": "140",   #af87d7
    "purple-3": "134",   #af5fd7
    "purple-4": "129",   #af00ff
    "purple-5": "92",    #8700d7

    "red-1": "217",      #ffafaf
    "red-2": "174",      #d78787
    "red-3": "167",      #d75f5f
    "red-4": "160",      #d70000

    "rose-1": "224",     #ffd7d7
    "rose-2": "204",     #ff5f87
    "rose-3": "197",     #ff005f

    "sky-1": "117",      #87d7ff
    "sky-2": "39",       #00afff
    "sky-3": "32",       #0087d7
    "sky-4": "25",       #005faf

    "slate-1": "103",    #8787af
    "slate-2": "60",     #5f5f87

    "brown-1": "138",    #af8787
    "brown-2": "131",    #af5f5f

    "teal-1": "50",      #00ffd7
    "teal-2": "37",      #00afaf
    "teal-3": "30",      #008787
    "teal-4": "23",      #005f5f

    "violet-1": "189",   #d7d7ff
    "violet-2": "141",   #af87ff
    "violet-3": "93",    #8700ff
    "violet-4": "57",    #5f00ff

    "yellow-1": "229",   #ffffaf
    "yellow-2": "220",   #ffd700
    "yellow-3": "136",   #af8700
    "yellow-4": "130",   #af5f00

    "black": "0",        #000000
    "gray-1": "235",     #262626
    "gray-2": "240",     #585858
    "gray-3": "246",     #949494
    "gray-4": "250",     #bcbcbc
    "white": "15",       #ffffff
}


ESC: str = "\x1b["
END: str = "m"

FG_COLOR: str = f"{ESC}38;5;[COLOR]{END}"
UNDERLINE_COLOR: str = f"{ESC}4;58;5;[COLOR]{END}"

BOLD = f"{ESC}1{END}"
DIM = f"{ESC}2{END}"
ITALIC = f"{ESC}3{END}"
UNDERLINE= f"{ESC}4{END}"
REVERSE = f"{ESC}7{END}"
STRIKEOUT = f"{ESC}9{END}"

RESET = f"{ESC}0{END}"


def style(
    *,
    fg: str = "",
    ul: str = "",
    bold: bool = False,  # b
    italic: bool = False,  # i
    underline: bool = False, # u
    strikeout: bool = False, # s
    reverse: bool = False,  # r
    dim: bool = False,  # d
) -> str:
    codes = []
    if fg:
        codes.append(FG_COLOR.replace("[COLOR]", COLORS[fg]))
    if ul:
        codes.append(UNDERLINE_COLOR.replace("[COLOR]", COLORS[ul]))

    if bold:
        codes.append(BOLD)
    if italic:
        codes.append(ITALIC)
    if reverse:
        codes.append(REVERSE)
    if underline:
        codes.append(UNDERLINE)
    if strikeout:
        codes.append(STRIKEOUT)
    if dim:
        codes.append(DIM)
    return "".join(codes)


COLORIZE = os.getenv("COLORTERM")
RX_OPEN = re.compile(r"""\<color
    (
        (\s+fg:(?P<fg>[a-z0-9-]+)) |
        (\s+ul:(?P<ul>[a-z0-9-]+))
    )*
    (\s+(?P<styles>[birdus]+))?
\s*\>""", re.IGNORECASE | re.VERBOSE)
RX_CLOSE = re.compile(r"\</color\>", re.IGNORECASE)


def colorize(text: str) -> str:
    """Format a string with color tags and return the formatted string.
    Does nothing if the `$COLORTERM` env variable is not set.

    The color tags are in the form of `fg:color` for foreground colors
    and `ul:color` for underline colors:

    ```
    <color fg:color ul:color birud>
      text
    </color>
    ```

    The tag can also have optional styles specified after the color name, separated by a space, and can be one or more of the following characters: `b` for bold, `i` for italic,`r` for reverse, `d` for dim, `u` for underline, and `s` for strikeout.
    The color can be any of the keys in the `COLORS` dictionary.
    """
    def repl(match: re.Match) -> str:
        if not COLORIZE:
            return ""
        fg_color = match.group("fg") or ""
        ul_color = match.group("ul") or ""
        styles = match.group("styles") or ""

        return style(
            fg=fg_color,
            ul=ul_color,
            bold="b" in styles,
            italic="i" in styles,
            reverse="r" in styles,
            dim="d" in styles,
            underline="u" in styles,
            strikeout="s" in styles,
        )

    text = RX_OPEN.sub(repl, text)
    text = RX_CLOSE.sub(RESET if COLORIZE else "", text)
    return text


if __name__ == "__main__":
    print()
    for color in COLORS:
        print(
            f"  {style(fg=color)}███ {color.ljust(9)}{RESET}"
            f"  {style(fg=color, bold=True)}bold{RESET}"
            f"  {style(fg=color, italic=True)}italic{RESET}"
            f"  {style(fg=color, reverse=True)}reverse{RESET}"
            f"  {style(fg=color, dim=True)}dim{RESET}"
            f"  {style(fg=color, underline=True)}underline{RESET}"
            f"  {style(fg=color, strikeout=True)}strikeout{RESET}"
        )
    print()
