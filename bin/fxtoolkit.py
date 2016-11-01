#!/usr/bin/python3
"""Script to poll FXCM servers for RSS-XML data.

Test

"""

# Standard imports
import os
import time
from pprint import pprint
from multiprocessing import Pool

# Import crawsiz libraries
from crawsiz.main import ingest
from crawsiz.main import feature
from crawsiz.utils import configuration
from crawsiz.utils import cli
from crawsiz.db import db_pair


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

        # Initialize filenames
        filepaths = []

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

            # Append filepath to list
            filepaths.append(filepath)

        # Create a pool of sub process resources
        with Pool(processes=5) as pool:
            # Create sub processes from the pool
            pool.map(ingest.ingest, filepaths)

        # Wait for all the processes to end
        pool.join()

    # Process data
    if cli_args.mode == 'process':
        # Initialize key variables
        lookahead = 1
        components = 10
        years = 6

        # Process data
        indices = db_pair.idx_all()
        for idx in indices:
            feature.process(idx, years=6, lookahead=1, components=10)

        # Create index page when all done
        _index()


def _pool_wrapper(argument_list):
    """Wrapper function to unpack arguments before calling the real function.

    Args:
        argument_list: A list of tuples of arguments to be
            provided to "feature.process" function

    Returns:
        Nothing

    """
    return feature.process(*argument_list)


def _index():
    """Create index.html page.

    Args:
        None

    Returns:
        None.

    """
    # Initialize key variables
    config = configuration.Config()
    directory = config.web_directory()
    filename = ('%s/index.html') % (directory)
    crosses = []
    links = ''

    # Get list of pair indexes
    indices = db_pair.idx_all()
    for idx in indices:
        crosses.append(db_pair.GetIDX(idx).pair())

    # Create links on index page
    for cross in sorted(crosses):
        links = (
            '%s<p><a href="%s.html">%s</a></p>\n'
            '') % (links, cross.lower(), cross.upper())

    # Create HTML
    html = ("""\
<html>
<head><title>Crawsiz</title></head>
<body>
<h1>Crawsiz</h1>
%s
</html></body>
""") % (links)

    # Write HTML to file
    with open(filename, 'w') as f_handle:
        f_handle.write(html)


if __name__ == '__main__':
    main()
