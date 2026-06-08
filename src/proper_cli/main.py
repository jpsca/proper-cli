import inspect
import sys
import textwrap
import typing as t
from inspect import isclass
from pathlib import Path
from signal import SIGTERM, signal
from sys import stderr

from .colors import colorize
from .parser import parse_args


__all__ = ("echo", "Cli")

HELP_OPT = "help"
INDENT = "  "
INITIAL_INDENT = " "


def echo(*texts: str, sep: str = " ") -> None:
    print(colorize(sep.join(texts)))


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


DEFAULT_COLORS = {
    "error": "fg:rose-3 b",
    "heading": "fg:amber-3",
    "path": "fg:lime-1",
    "command": "fg:lime-2",
    "args": "fg:amber-1",
    "options": "fg:gray-3",
}

class Cli:
    _parent: str
    _indent_level: int
    _show_params: bool
    _env: dict

    def __init__(
        self,
        *,
        parent: str = "",
        indent: str = INDENT,
        initial_indent: str = INITIAL_INDENT,
        indent_start: int = 0,
        show_params: bool = True,
        colors: dict[str, str] | None = None,
        **env,
    ) -> None:
        self._parent = parent
        self._indent_level = indent_start
        self._indent_by = indent
        self._indent_plus = initial_indent
        self._show_params = show_params
        self._colors = colors or DEFAULT_COLORS
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

    # ---- Private ----

    def _echo(self, *text: str, indentation: int = 0) -> None:
        indent = self._indent(indentation)
        for line in text:
            echo(f"{indent}{line}")

    def _indent(self, plus_level: int = 0) -> str:
        level = self._indent_level + plus_level
        return self._indent_plus + (self._indent_by * level)

    def _run(self, *args, **opts) -> None:
        if not args:
            return self._help()

        name, *args = args
        cmd = getattr(self, name, None)
        if not cmd:
            return self._command_not_found(name)

        if isclass(cmd):
            return self._run_subgroup(name, cmd, args, opts)
        return self._run_command(name, cmd, args, opts)

    def _command_not_found(self, name: str) -> None:
        self._echo(f"\n<color {self._colors['error']}> Command `{name}` not found </color>")
        self._help()

    def _init_subgroup(
        self,
        name: str,
        cls: type,
        indent_level: int = 0,
    ) -> "Cli":
        return cls(
            parent=f"{self._parent} {name}",
            indent_start=indent_level,
            show_params=self._show_params,
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
        name: str,
        cmd: t.Callable,
        args: list[str],
        opts: dict[str, t.Any],
    ) -> None:
        if HELP_OPT in opts:
            return self._help_command(name, cmd)

        if not self._has_required_params(cmd, *args, **opts):
            self._echo(f"\n<color {self._colors['error']}>--- Missing required parameters ---</color>")
            self._help_command(name, cmd)
            return

        return cmd(*args, **opts)

    def _help(self) -> None:
        self._help_intro()
        self._help_header()
        self._help_body()
        print()

    def _help_intro(self) -> None:
        doc = get_doc(self)
        if doc:
            intro = textwrap.indent(doc.strip(), self._indent())
            self._echo(f"\n{intro}")

    def _help_header(self) -> None:
        print()
        self._echo(f"<color {self._colors['heading']}>Usage:</color>\n")
        self._echo(
            f"{self._parent} <color {self._colors['command']}><command></color> <color {self._colors['args']}>[args]</color> <color {self._colors['options']}>[options]</color>\n",
            "Run any command with the --help option for more information.",
            "All the options are optional and can be specified in any order.",
             indentation=1,
        )
        print()
        self._echo(f"<color {self._colors['heading']}>Available Commands:</color>\n")

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
        signature = self._get_signature(name, cmd)

        self._echo(signature, indentation=1)
        self._echo(cmd_help, indentation=4)

    def _help_command(self, name: str, cmd: t.Callable) -> None:
        signature = self._get_signature(name, cmd)
        doc = textwrap.indent(get_doc(cmd), self._indent())
        print()
        self._echo(f"{signature}\n\n{doc}")

    def _get_signature(self, name: str, cmd: t.Callable) -> str:
        parent = " ".join(self._parent.split(" ")[1:])
        if parent:
            parent = f"<color {self._colors['path']}>{parent}</color> "

        signature = f"{parent}<color {self._colors['command']}>{name}</color>"

        if self._show_params:
            args, options = self._get_params(cmd)
            if args:
                signature = f"{signature} <color {self._colors['args']}>{args}</color>"
            if options:
                signature = f"{signature} <color {self._colors['options']}>{options}</color>"

        return signature.strip()

    def _get_params(self, cmd: t.Callable) -> tuple[str, str]:
        sig = inspect.signature(cmd)
        args = []
        options = []

        for name, pp in sig.parameters.items():
            if name in ("self", "cls"):
                continue
            # Secret parameter
            if name.startswith("_"):
                continue

            if pp.default is pp.empty:
                args.append(name)
            elif isinstance(pp.default, bool):
                options.append(f"--{name}")
            else:
                options.append(f"--{name}={repr(pp.default)}")

        return " ".join(args), " ".join(options)

    def _get_required_params(self, cmd: t.Callable) -> list[str]:
        sig = inspect.signature(cmd)
        required = []

        for name, pp in sig.parameters.items():
            if name in ("self", "cls"):
                continue
            # Secret parameter
            if name.startswith("_"):
                continue

            if pp.default is pp.empty:
                required.append(name)

        return required

    def _has_required_params(self, cmd: t.Callable, *args, **kwargs) -> bool:
        required = self._get_required_params(cmd)
        if not required:
            return True
        num_required = len(required)
        for name in required:
            if name in kwargs:
                num_required -= 1
        return len(args) >= num_required
