import typing as t


def ask(question: str, default: t.Any = None, alternatives: str = "") -> t.Any:
    """Ask a question via input() and return their answer.

    Arguments:
    - question (str): The text of the question.
    - default (any): Default value if no answer is provided.
    - alternatives (str): Alternatives to display. eg: "Y/n"
    """
    ops = alternatives or default
    question += f" [{str(ops)}] " if ops else ""
    while True:
        resp = input(question)
        if resp:
            return resp
        if default is not None:
            return default


YES_CHOICES: tuple[str, ...] = ("y", "yes", "t", "true", "on", "1")
NO_CHOICES: tuple[str, ...] = ("n", "no", "f", "false", "off", "0")


def confirm(
    question: str,
    default: bool = False,
    yes_choices: t.Sequence[str] = YES_CHOICES,
    no_choices: t.Sequence[str] = NO_CHOICES,
) -> bool:
    """Ask a yes/no question via proper_cli.ask() and return their answer.

    Arguments:
    - question (str): Prompt question
    - default (bool): Default value if no answer is provided.
    - yes_choices (list): Default 'y', 'yes', '1', 'on', 'true', 't'
    - no_choices (list): Default 'n', 'no', '0', 'off', 'false', 'f'

    """
    yes_choices = yes_choices or YES_CHOICES
    no_choices = no_choices or NO_CHOICES

    default_value = yes_choices[0] if default else no_choices[0]
    if default is None:
        options = f"{yes_choices[0]}|{no_choices[0]}"
    else:
        if default:
            options = f"{yes_choices[0].title()}/{no_choices[0]}"
        else:
            options = f"{yes_choices[0]}/{no_choices[0].title()}"

    while True:
        resp = ask(question, default_value, options)
        if default is not None:
            resp = resp or str(default)
        resp = resp.lower()
        if resp in yes_choices:
            return True
        if resp in no_choices:
            return False
