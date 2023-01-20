import inspect
import sys
import textwrap
import typing as t
from inspect import isclass
from pathlib import Path
from signal import SIGTERM, signal
from sys import stderr

from . import pastel
from .pastel import add_style  # noqa
from .parser import parse_args


__all__ = ("echo", "add_style", "Cli")

INDENT_START_LEVEL = 1
HELP_OPT = "help"
INDENT = "  "


def echo(*texts: str, sep: str = " ") -> None:
    print(pastel.colorize(sep.join(texts)))


def sigterm_handler(*args) -> None:
    raise SystemExit(1)


def get_doc(cmd: t.Callable) -> str:
    """Extract and dedent the __doc__ of a method/function.

    Unlike `textwrap.dedent()` it also works when the first line
    is not indented.
    """
    doc = cmd.__doc__
    if not doc:
        return ""

    # doc has only one line
    if "\n" not in doc:
        return doc

    # Only Python core devs write __doc__ like this
    if doc.startswith(("\n", "\\\n")):
        return textwrap.dedent(doc)

    # First line is not indented
    first, rest = doc.split("\n", 1)
    return first + "\n" + textwrap.dedent(rest)


class Cli:
    _indent_level: int
    _parent: str
    _echo: t.Callable
    _env: dict

    def __init__(
        self,
        *,
        parent: str = "",
        indent_level: int = INDENT_START_LEVEL,
        **env,
    ) -> None:
        self._parent = parent
        self._indent_level = indent_level
        self._echo = echo
        self._env = env

    def __call__(self) -> None:
        signal(SIGTERM, sigterm_handler)

        try:
            parent, *sysargs = sys.argv
            self._parent = Path(parent).stem
            args, opts = parse_args(sysargs)
            self._run(*args, **opts)
        except KeyboardInterrupt:
            stderr.write("\n")
            exit(1)

    @property
    def _commands(self):
        commands = {}
        names = [name for name in self.__dir__() if not name.startswith("_")]
        for name in names:
            cmd = getattr(self, name, None)
            if inspect.isclass(cmd):
                continue
            commands[name] = cmd
        return commands

    @property
    def _subgroups(self):
        subgroups = {}
        names = [name for name in self.__dir__() if not name.startswith("_")]
        for name in names:
            cls = getattr(self, name, None)
            if not inspect.isclass(cls):
                continue
            subgroups[name] = cls
        return subgroups

    @property
    def _indent(self) -> str:
        return INDENT * self._indent_level

    # Private

    def _run(self, *args, **opts) -> None:
        cmd = None
        if not args:
            return self._help()

        name, *args = args
        cmd = getattr(self, name, None)
        if not cmd:
            return self._command_not_found(name)

        if isclass(cmd):
            return self._run_subgroup(name, cmd, args, opts)
        return self._run_command(cmd, args, opts)

    def _command_not_found(self, name: str) -> None:
        self._echo(f"\n<error> Command `{name}` not found </error>")
        self._help()

    def _init_subgroup(
        self,
        name: str,
        cls: type,
        indent_level: int = INDENT_START_LEVEL,
    ) -> "Cli":
        return cls(
            parent=f"{self._parent} {name}",
            indent_level=indent_level,
            **self._env,
        )

    def _run_subgroup(
        self,
        name: str,
        cls: type,
        args: list[str],
        opts: dict[str, t.Any],
    ) -> None:
        cli = self._init_subgroup(name, cls)
        if not args:
            if not opts or opts == {HELP_OPT: True}:
                return cli._help()
        return cli._run(*args, **opts)

    def _run_command(
        self,
        cmd: t.Callable,
        args: list[str],
        opts: dict[str, t.Any],
    ) -> None:
        if HELP_OPT in opts:
            return self._help_command(cmd)
        return cmd(*args, **opts)

    def _help(self, header: bool = True) -> None:
        self._help_intro()
        self._help_header()
        self._help_body()
        print()

    def _help_intro(self) -> None:
        doc = get_doc(self)
        if doc:
            intro = textwrap.indent(doc.strip(), " ")
            self._echo(f"\n{intro}")

    def _help_header(self) -> None:
        self._echo("\n <fg=yellow>Usage:</>")
        self._echo(f" {self._indent}{self._parent} <command> [args] [options]\n")
        self._echo(
            f" {self._indent}"
            "Run any command with the --help option for more information."
        )
        self._echo("\n <fg=yellow>Available Commands:</>")

    def _help_body(self) -> None:
        for name, cmd in self._commands.items():
            self._help_list_command(name, cmd)
        for name, cls in self._subgroups.items():
            self._help_list_subgroup(name, cls)

    def _help_list_subgroup(self, name: str, cls: type) -> None:
        print()
        cli = self._init_subgroup(name, cls, indent_level=self._indent_level)
        cli._help_body()

    def _help_list_command(self, name: str, cmd: t.Callable) -> None:
        doc = cmd.__doc__ or ""
        cmd_help = doc.strip().split("\n")[0]

        indent = self._indent
        parent = " ".join(self._parent.split(" ")[1:])
        if parent:
            parent = f"<fg=green>{parent}</> "

        self._echo(
            f" {indent}{parent}<fg=light_green>{name}</>\n"
            f" {INDENT * 5}{cmd_help}"
        )

    def _help_command(self, cmd: t.Callable) -> None:
        print()
        doc = get_doc(cmd)
        self._echo(textwrap.indent(doc, " "))
