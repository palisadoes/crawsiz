"""Library to process the ingest of data files."""

import csv
import sys
import os
import re
import time
import datetime
import zipfile
import shutil

# Append custom application libraries
from crawsiz.utils import configuration
from crawsiz.utils import log


__author__ = 'Peter Harrison (Colovore LLC.) <peter@colovore.com>'
__version__ = '0.0.1'


class Valid(object):
    """Class Checks the validity of an ingest file.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, filepath):
        """Function for intializing the class.

        Args:
            filepath: Config file to use
            die: Die if filepath is invalid.

        Returns:
            None

        """
        # Initialize key variables
        self.filepath = filepath


    def pair(self):
        """Determine the pair represented in the file.

        Args:
            None

        Returns:
            result: Pair

        """
        # Initialize key variables
        result = None
        validity = True
        config = configuration.Config()

        # Extract symbol from filename
        filename = os.path.basename(self.filepath)
        regex = re.compile(r'^([A-Z]{6})\d+.csv$')
        match = regex.search(filename)

        # Fail if invalid filename
        if bool(match) is False:
            log_message = (
                'File "%s" has invalid name. '
                '') % (self.filepath)
            log.log2warn(1003, log_message)
            validity = False
        else:
            # Fail if invalid pair
            pair = match.group(1).upper()
            if config.valid_pair(pair) is False:
                log_message = (
                    'Pair "%s" in filename %s is invalid. '
                    'Not in config file.'
                    '') % (pair, self.filepath)
                log.log2warn(1002, log_message)
                validity = False

        # Get symbol name for file
        if validity is True:
            result = match.group(1).upper()

        # Return
        return result

    def valid(self):
        """Determine whether file is valid.

        Args:
            None

        Returns:
            validity: True if valid

        """
        # Initialize key variables
        validity = True

        # Invalid if pair not found
        if self.pair() is None:
            validity = False

        # Fail if filepath doesn't exist
        if os.path.exists(self.filepath) is False:
            log_message = (
                'File %s does not exist.'
                '') % (self.filepath)
            log.log2warn(1004, log_message)
            validity = False
            return validity

        # Fail if filepath doesn't exist
        if os.path.isfile(self.filepath) is False:
            log_message = (
                'Expected %s to be a file. It is not.'
                '') % (self.filepath)
            log.log2warn(1005, log_message)
            validity = False
            return validity

        # Return
        return validity


class Ingest(object):

    """Class ingests file data to update the database.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, filepath):
        """Function for intializing the class.

        Args:
            filepath: Config file to use

        Returns:
            None

        """
        # Initialize key variables
        self.filepath = filepath

        # Die if file is invalid
        validity = Valid(filepath)
        if validity.valid() is False:
            log_message = (
                'File %s is invalid.'
                '') % (self.filepath)
            log.log2die(1006, log_message)

        # Get the pair
        self.pair = validity.pair()

    def ingest(self):
        """Ingest file.

        Args:
            filename: Name of file to ingest
            archive: Archive filename if True

        Returns:
            timeframe: Timeframe in minutes

        """
        # Initialize key variables
        data = []

        ######################################################################
        # Convert data
        ######################################################################

        with open(self.filepath, newline='') as csvfile:
            lines = csv.reader(csvfile, delimiter=',', quotechar='|')
            for line in lines:
                # Get the time
                r_time = line[1]

                # Skip if time doesn't end in ":00"
                if r_time.endswith(':00') is False:
                    continue

                # Get data
                r_day = line[0]
                r_date = ('%s %s') % (r_day, r_time)
                r_open = float(line[2])
                r_high = float(line[3])
                r_low = float(line[4])
                r_close = float(line[5])
                r_volume = int(line[6])

                # Convert date to timestamp
                timestamp = int(time.mktime(datetime.datetime.strptime(
                    r_date, "%Y.%m.%d %H:%M").timetuple()))

                print(', '.join(line))

        """
        # Read file
        with open(filename, 'r') as f_handle:
            for nextline in f_handle:
                # Split line
                line = nextline.split(',')

                # Get data
                r_date = ('%s %s') % (line[0], line[1])
                r_open = float(line[2])
                r_high = float(line[3])
                r_low = float(line[4])
                r_close = float(line[5])
                r_volume = int(line[6])

                # Convert date to timestamp
                timestamp = int(time.mktime(datetime.datetime.strptime(
                    r_date, "%Y.%m.%d %H:%M").timetuple()))

                # Append data
                row = [self.pair, timestamp, r_open,
                       r_close, r_high, r_low, r_volume]
                data.append(row)
        """

        return None


def _update_database(data=None, config_file=None, timeframe=None):
    """Update databse with data.

    Args:
        data: List of lists representing data from the file
            [[symbol, timestamp, open, close, high, low, volume],
             [symbol, timestamp, open, close, high, low, volume],
             [symbol, timestamp, open, close, high, low, volume]]
        config_file: Configuration filename
        timeframe: Timeframe data belongs to

    Returns:
        None

    """
    # Initialize key variables
    sql_statement = (
        'REPLACE INTO fx_%s '
        '(symbol, timestamp, open, close, high, low, volume) '
        ' VALUES ') % (timeframe)
    sql_statement = ('%s %s') % (
        sql_statement, '(%s, %s, %s, %s, %s, %s, %s)')

    # Create database object
    database = db.Database(config_file=config_file)

    # Do SQL update
    database.db_modify(sql_statement, 'AB-0010', data_list=data)


def _archive_ingest_file(config_file, filepath):
    """Update databse with data.

    Args:
        config_file: Config file to use
        filepath: File to zip

    Returns:
        zip_filename: Filename of archive

    """
    # Initialize key variables
    config = configuration.ProcessConfig(config_file=config_file)
    archive_directory = config.ingest_archive_directory()
    timestamp = int(time.time())

    # Create target filename
    filename = os.path.basename(filepath)
    target_filename = ('%s/%s') % (archive_directory, filename)

    # Create zip filename
    zip_filename = ('%s.%s.zip') % (
        target_filename,
        datetime.datetime.fromtimestamp(
            timestamp).strftime('%Y%m%d-%H%M%S'))

    # Move file
    shutil.move(filepath, target_filename)

    # Archive file
    zip_handle = zipfile.ZipFile(zip_filename, mode='w')
    zip_handle.write(target_filename)
    zip_handle.close()

    # Delete ingest file
    os.remove(target_filename)

    # Return zip filename
    return zip_filename
