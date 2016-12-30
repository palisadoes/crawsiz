#!/usr/bin/python3
"""Script to poll FXCM servers for RSS-XML data.

Test

"""

# Standard imports
import os
import time
from multiprocessing import Pool
import multiprocessing

# Import crawsiz libraries
from crawsiz.main import ingest
from crawsiz.main import feature
from crawsiz.utils import configuration
from crawsiz.utils import cli
from crawsiz.db import db_pair


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
        idx_ingested_list = _autoingest()
        if bool(idx_ingested_list) is True:
            _process(idx_ingested_list)

    # Process data
    if cli_args.mode == 'process':
        _process()


def _autoingest():
    """Autoingest data.

    Args:
        None

    Returns:
        idx_ingested: List of indexes that were updated

    """
    # Get config
    config = configuration.Config()

    # Initialize filenames
    filepaths = []
    pairs = []
    idx_ingested = []
    available_cores = min(1, multiprocessing.cpu_count() - 1)

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
        pairs.append(filecheck.pair())

    # Create a pool of sub process resources
    with Pool(processes=available_cores) as pool:
        # Create sub processes from the pool
        pool.map(ingest.ingest, filepaths)

    # Wait for all the processes to end
    pool.join()

    # Get a list of all pair indices in the database
    idx_all = db_pair.idx_all()
    for idx in idx_all:
        db_object = db_pair.GetIDX(idx)
        next_pair = db_object.pair()
        if next_pair in pairs:
            idx_ingested.append(idx)

    # Return
    if bool(idx_ingested) is False:
        idx_ingested = None
    return idx_ingested


def _process(idx_ingested_list=None):
    """Process crosses in database.

    Args:
        idx_ingested_list: List of pair indices that were ingested.

    Returns:
        None

    """
    # Initialize key variables
    config = configuration.Config()
    lookahead = config.lookahead()
    components = 10
    years = 6
    argument_list = []
    available_cores = min(1, multiprocessing.cpu_count() - 1)

    # Process data
    if idx_ingested_list is None:
        indices = db_pair.idx_all()
    else:
        indices = idx_ingested_list
    for idx in indices:
        argument_list.append(
            (idx, years, lookahead, components)
        )

    # Create a pool of sub process resources
    with Pool(processes=available_cores) as pool:
        # Create sub processes from the pool
        pool.map(_pool_wrapper, argument_list)

    # Wait for all the processes to end
    pool.join()

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
        config: Configuration object

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
