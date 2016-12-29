"""Library to process the ingest of data files."""

import csv
import os
import re
import time
from datetime import datetime
import zipfile
import shutil

# Append custom application libraries
from crawsiz.utils import configuration
from crawsiz.utils import general
from crawsiz.utils import log
from crawsiz.db import db_pair
from crawsiz.db import db
from crawsiz.db.db_orm import Data, Pair


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
        regex = re.compile(r'^([A-Z]{6})1440.csv$')
        match = regex.search(filename)

        # Fail if invalid filename
        if bool(match) is False:
            if filename.lower().endswith('.csv') is True:
                log_message = (
                    'File "%s" has invalid name. '
                    '') % (self.filepath)
                log.log2warn(1003, log_message)
                validity = False
            else:
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

        # Fail if filepath is not a file
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
        datapoints = []
        max_timestamp = 0

        # Get the last update time for the pair
        last_updated = self._last_updated()

        # Get pair IDX value
        idx_pair = db_pair.GetPair(self.pair).idx()

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
                timestamp = general.utc_timestamp(
                    datetime.strptime(r_date, "%Y.%m.%d %H:%M")
                    )

                # Skip if data is stale
                if timestamp <= last_updated:
                    continue

                # Skip data if it is not on a UTC day boundary
                if timestamp % 86400 != 0:
                    continue

                # Assign values to database object
                datapoint = Data(
                    idx_pair=idx_pair,
                    fxopen=r_open,
                    fxclose=r_close,
                    fxhigh=r_high,
                    fxlow=r_low,
                    fxvolume=r_volume,
                    timestamp=timestamp
                )
                datapoints.append(datapoint)

                # Assign max_timestamp
                max_timestamp = max(timestamp, max_timestamp)

        # Update only if we have data
        if bool(datapoints) is True:
            # Update Data table
            database = db.Database()
            database.add_all(datapoints, 9999)

            # Update last updated for Pair
            database = db.Database()
            session = database.session()
            result = session.query(Pair).filter(
                Pair.pair == self.pair.encode()).one()
            result.last_timestamp = max_timestamp
            session.commit()
            database.close()

            # Archive the ingest file
            _archive_ingest_file(self.filepath)

    def _last_updated(self):
        """Get the timestamp for the last database update for the pair.

        Args:
            None

        Returns:
            last_updated: Epoch GMT timestamp

        """
        # Get the last update time for the pair
        if db_pair.pair_exists(self.pair) is True:
            # Get the last updated time
            last_updated = db_pair.GetPair(self.pair).last_timestamp()
        else:
            # Prepare SQL query to read a record from the database.
            record = Pair(pair=general.encode(self.pair))
            database = db.Database()
            database.add(record, 1081)

            # Define the last updated time
            last_updated = 0

        # Return
        return last_updated


def _archive_ingest_file(filepath):
    """Update databse with data.

    Args:
        filepath: File to zip

    Returns:
        zip_filename: Filename of archive

    """
    # Initialize key variables
    config = configuration.Config()
    archive_directory = config.archive_directory()
    timestamp = int(time.time())

    # Create target filename
    filename = os.path.basename(filepath)
    target_filename = ('%s/%s') % (archive_directory, filename)

    # Create zip filename
    zip_filename = ('%s.%s.zip') % (
        target_filename,
        datetime.fromtimestamp(
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


def ingest(filepath):
    """Ingest file.

    Args:
        filepath: Name of file to ingest

    Returns:
        None

    """
    # Initialize key variables
    ingest_object = Ingest(filepath)
    ingest_object.ingest()
