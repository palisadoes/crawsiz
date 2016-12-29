#!/usr/bin/python3
"""XML processing CLI class."""

import textwrap
import argparse
import sys

# Import custom libraries
from crawsiz.utils import log


class ProcessCli(object):
    """Class gathers all CLI information.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        get_cli:
    """

    def __init__(self, additional_help=None):
        """Function for intializing the class."""
        # Create a number of here-doc entries
        if additional_help is not None:
            self.config_help = additional_help
        else:
            self.config_help = ''

    def get_cli(self):
        """Return all the CLI options.

        Args:
            self:

        Returns:
            args: Namespace() containing all of our CLI arguments as objects
                - filename: Path to the configuration file

        """
        # Initialize key variables
        width = 80

        # Log the cli command
        log_message = ('CLI: %s') % (' '.join(sys.argv))
        log.log2quiet(1000, log_message)

        # Header for the help menu of the application
        parser = argparse.ArgumentParser(
            description=self.config_help,
            formatter_class=argparse.RawTextHelpFormatter)

        # Add subparser
        subparsers = parser.add_subparsers(dest='mode')

        # Parse "autoingest", return object used for parser
        _cli_autoingest(subparsers, width=width)

        # Parse "process", return object used for parser
        _cli_process(subparsers, width=width)

        # Return the CLI arguments
        args = parser.parse_args()

        # Return our parsed CLI arguments
        return args


def _cli_autoingest(subparsers, width=80):
    """Process "autoingest" CLI commands.

    Args:
        subparsers: Subparsers object
        width: Width of the help text string to STDIO before wrapping

    Returns:
        None

    """
    # Initialize key variables
    parser = subparsers.add_parser(
        'autoingest',
        help=textwrap.fill(
            'autoingest FX data from file.', width=width)
    )

    # Process archive flag
    parser.add_argument(
        '--archive',
        dest='archive',
        action="store_true",
        default=False,
        help=textwrap.fill(
            'Flag to archive autoingested data file', width=width)
    )


def _cli_process(subparsers, width=80):
    """Process "process" CLI commands.

    Args:
        subparsers: Subparsers object
        width: Width of the help text string to STDIO before wrapping

    Returns:
        None

    """
    # Initialize key variables
    parser = subparsers.add_parser(
        'process',
        help=textwrap.fill(
            'Process FX data from database.', width=width)
    )
