import typing as t
from collections.abc import Sequence


NEGATIVE_FLAG_PREFIX = "no-"


def parse_args(
    cliargs: Sequence[str],
) -> tuple[list[str], dict[str, t.Any]]:  # noqa: C901
    """Parse the command line arguments and return a list of the positional
    arguments and a dictionary with the named ones.

        >>> parse_args(["abc", "def", "-w", "3", "--foo", "bar", "-narf=zort"])
        (['abc', 'def'], {'w': '3', 'foo': 'bar', 'narf': 'zort'})

        >>> parse_args(["-abc"])
        ([], {'abc': True})

        >>> parse_args(["-no-abc"])
        ([], {'abc': False})

        >>> parse_args(["-f", "1", "-f", "2", "-f", "3"])
        ([], {'f': ['1', '2', '3']})

    """
    # Split the "key=arg" arguments
    largs = []
    for arg in cliargs:
        if arg.startswith("-") and "=" in arg:
            key, arg = arg.split("=", 1)
            largs.append(key)
        largs.append(arg)

    args = []
    flags = []
    kwargs = {}
    key = None
    for sarg in largs:
        if is_key(sarg):
            if key is not None:
                flags.append(key)
            key = sarg.strip("-")
            continue

        if not key:
            args.append(sarg)
            continue

        if key in kwargs:
            value = kwargs[key]
            if isinstance(value, list):
                value.append(sarg)
            else:
                value = [value, sarg]
            kwargs[key] = value
        else:
            kwargs[key] = sarg

    # Get the flags
    if key:
        flags.append(key)
    # An extra key without a value is a flag if it has not been used before.
    # Otherwise is a typo.
    for flag in flags:
        if flag in kwargs:
            continue
        if flag.startswith(NEGATIVE_FLAG_PREFIX):
            flag = flag[len(NEGATIVE_FLAG_PREFIX) :]
            kwargs[flag] = False
        else:
            kwargs[flag] = True

    return args, kwargs


def is_key(sarg: str) -> bool:
    """Check if `sarg` is a key (eg. -foo, --foo) and not a negative
    number (eg. -33, -3.14)."""
    if not sarg.startswith("-"):
        return False
    if sarg.startswith("--"):
        return True
    return not _is_number(sarg)


def _is_number(sarg: str) -> bool:
    try:
        float(sarg)
    except ValueError:
        return False
    return True
