#  Copyright 2020-2024 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
import click
from skytemple_randomizer.config import version as version_string
from skytemple_randomizer.frontend.cli import init as init_cli


@click.group()
def main():
    pass


@main.command(help="Print version and exit.")
def version():
    click.echo(version_string())


@main.command(
    help="Start the GUI application, with optional ROM path argument.",
    context_settings=dict(
        ignore_unknown_options=True,
    ),
    add_help_option=False,
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def gui(args):
    from skytemple_randomizer.frontend.gtk.main import main

    main(["skytemple_randomizer gui"] + list(args))


@main.group(help="Command Line API. See CLI_API.md for documentation.")
def cli():
    pass


init_cli(cli)


if __name__ == "__main__":
    main()
