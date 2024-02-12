import sys

from proper_cli import Cli


class Foo(Cli):
    def bar(self):
        """BAR"""
        pass


class Lorem(Cli):
    """Lorem ipsum is placeholder text commonly used for previewing
    layouts and visual mockups."""

    def ipsum(self, x, y=3):
        """IPSUM

        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
        commodo consequat.
        """
        pass

    def sit(self, meh=False):
        """SIT"""
        pass


class Manager(Cli):
    """Hello World!
    """

    def a(self):
        """AAA"""
        pass

    def b(self):
        """BBB"""
        pass

    def _c(self):
        """CCC"""

    foo = Foo
    lorem = Lorem


def test_main_help(get_out_text):
    cli = Manager()
    sys.argv = ["manage.py", "--help"]
    cli()

    assert get_out_text() == """
 Hello World!

 Usage:

   manage <command> [args] [options]

   Run any command with the --help option for more information.

 Available Commands:

   a
         AAA
   b
         BBB

   foo bar
         BAR

   lorem ipsum x [--y=3]
         IPSUM
   lorem sit [--meh]
         SIT

"""


def test_disable_params(get_out_text):
    cli = Manager(show_params=False)
    sys.argv = ["manage.py", "--help"]
    cli()

    assert get_out_text() == """
 Hello World!

 Usage:

   manage <command> [args] [options]

   Run any command with the --help option for more information.

 Available Commands:

   a
         AAA
   b
         BBB

   foo bar
         BAR

   lorem ipsum
         IPSUM
   lorem sit
         SIT

"""


def test_subgroup_help(get_out_text):
    cli = Manager()
    sys.argv = ["manage.py", "lorem"]
    cli()

    assert get_out_text() == """
 Lorem ipsum is placeholder text commonly used for previewing
 layouts and visual mockups.

 Usage:

   manage lorem <command> [args] [options]

   Run any command with the --help option for more information.

 Available Commands:

   lorem ipsum x [--y=3]
         IPSUM
   lorem sit [--meh]
         SIT

"""


def test_disble_params_in_subgroup_help(get_out_text):
    cli = Manager(show_params=False)
    sys.argv = ["manage.py", "lorem"]
    cli()

    assert get_out_text() == """
 Lorem ipsum is placeholder text commonly used for previewing
 layouts and visual mockups.

 Usage:

   manage lorem <command> [args] [options]

   Run any command with the --help option for more information.

 Available Commands:

   lorem ipsum
         IPSUM
   lorem sit
         SIT

"""


def test_command_help(get_out_text):
    cli = Manager()
    sys.argv = ["manage.py", "lorem", "ipsum", "--help"]
    cli()

    assert get_out_text() == """
 lorem ipsum x [--y=3]

 IPSUM

 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
 tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
 veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
 commodo consequat.

"""


def test_hidden_command_has_help(get_out_text):
    cli = Manager()
    sys.argv = ["manage.py", "_c", "--help"]
    cli()

    assert get_out_text() == """
 _c

 CCC
"""
