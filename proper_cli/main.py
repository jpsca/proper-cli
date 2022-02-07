import sys
from inspect import isclass
from pathlib import Path
from signal import SIGTERM, signal
from sys import stderr

from . import pastel
from .help_mixin import HELP_OPT, HelpMixin
from .parser import parse_args


__all__ = ("echo", "add_style", "Cli")

INDENT_START_LEVEL = 1


def echo(*texts, sep=" "):
    print(pastel.colorize(sep.join(texts)))


def add_style(self, name, fg=None, bg=None, options=None):
    pastel.add_style(name, fg=fg, bg=bg, options=options)


def sigterm_handler(_, __):
    raise SystemExit(1)


class Cli(HelpMixin):
    def __init__(self, *, parent="", indent_level=INDENT_START_LEVEL, **env):
        self._parent = parent
        self._indent_level = indent_level
        self._env = env
        self._echo = echo
        self._add_style = add_style

    def __call__(self, *, default=None):
        signal(SIGTERM, sigterm_handler)

        try:
            parent, *sysargs = sys.argv
            self._parent = Path(parent).stem
            args, opts = parse_args(sysargs)
            self._run(*args, **opts)
        except KeyboardInterrupt:
            stderr.write("\n")
            exit(1)

    # Private

    def _run(self, *args, **opts):
        cmd = None
        if not args:
            return self._help()

        name, *args = args
        cmd = getattr(self, name, None)
        if not cmd:
            return self._command_not_found(name)

        if isclass(cmd):
            return self._run_subcommand(name, cmd, args, opts)
        return self._run_command(cmd, args, opts)

    def _command_not_found(self, name):
        self._echo(f"\n<error> Command `{name}` not found </error>")
        self._help()

    def _init_subcommand(self, name, cls, indent_level=INDENT_START_LEVEL):
        return cls(
            parent=f"{self._parent} {name}", indent_level=indent_level, **self._env
        )

    def _run_subcommand(self, name, cls, args, opts):
        cli = self._init_subcommand(name, cls)
        if not args:
            if not opts or opts == {HELP_OPT: True}:
                return cli._help()
        return cli._run(*args, **opts)

    def _run_command(self, cmd, args, opts):
        if HELP_OPT in opts:
            return self._help_command(cmd)
        return cmd(*args, **opts)
