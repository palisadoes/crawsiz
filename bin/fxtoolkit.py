#!/usr/bin/python3
"""Script to poll FXCM servers for RSS-XML data.

Test

"""

import os
import sys
import re
import time

# Import crawsiz libraries
from crawsiz.main import ingest
from crawsiz.utils import configuration
from crawsiz.utils import cli
from crawsiz.utils import general
from crawsiz.utils import log
from crawsiz.db import db
from crawsiz.db import db_pair
from crawsiz.db.db_orm import Pair


__author__ = 'Peter Harrison (Colovore LLC.) <peter@colovore.com>'
__version__ = '0.0.1'


def main():
    """Format Nagios host configuration.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    additional_help = """\
This processes XML data from FXCM http:// feeds.

"""

    # Process the CLI
    cli_object = cli.ProcessCli(additional_help=additional_help)
    cli_args = cli_object.get_cli()

    # Autoingest stuff
    if cli_args.mode == 'autoingest':
        # Get config
        config = configuration.Config()

        # Get list of files in ingest directory
        for filename in os.listdir(config.ingest_directory()):
            # Get next filename from list
            filepath = ('%s/%s') % (config.ingest_directory(), filename)

            # Get age of file
            age = int(time.time() - os.path.getmtime(filepath))

            # Only proceed if file is old enough
            if age < 15:
                continue

            # Don't process invalid files
            filecheck = ingest.Valid(filepath)
            if filecheck.valid() is False:
                continue

            # Insert pair in database if it doesn't exist
            pair = filecheck.pair()
            if db_pair.pair_exists(pair) is False:
                # Prepare SQL query to read a record from the database.
                record = Pair(pair=general.encode(pair))
                database = db.Database()
                database.add(record, 1081)

            # Ingest data
            ingest_object = ingest.Ingest(filepath)
            ingest_object.ingest()
            continue

            if cli_args.filetype == 1:
                timeframe = ingest_object.ingest_type_01_file(
                    filename=filepath, archive=cli_args.archive)


if __name__ == '__main__':
    main()
