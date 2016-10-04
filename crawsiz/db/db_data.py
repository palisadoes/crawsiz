"""Module of crawsiz database functions.

Classes for agent data

"""
# Python standard libraries
from sqlalchemy import and_

# Infoset libraries
from crawsiz.utils import log
from crawsiz.db import db
from crawsiz.db.db_orm import Data
from crawsiz.db import db_pair


class GetIDX(object):
    """Class to return agent data.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, idx, ts_start, ts_stop):
        """Function for intializing the class.

        Args:
            idx: idx of datapoint
            ts_start: Starting timestamp
            ts_stop: Ending timestamp

        Returns:
            None

        """
        # Initialize important variables
        self.data_fxhigh = []
        self.data_fxlow = []
        self.data_fxclose = []
        self.data_fxvolume = []
        self.data_timestamp = []

        # Fix edge cases
        if ts_start > ts_stop:
            ts_start = ts_stop

        # Make sure pair idx exists
        if db_pair.idx_exists(idx) is False:
            log_message = ('idx %s not found.') % (idx)
            log.log2die(1049, log_message)

        # Establish a database session
        database = db.Database()
        session = database.session()
        result = session.query(Data).filter(and_(
            Data.timestamp >= ts_start,
            Data.timestamp <= ts_stop,
            Data.idx_pair == idx)).order_by(Data.timestamp)

        # Return the session to the database pool after processing
        session.close()

        # Massage data
        for instance in result:
            self.data_fxhigh.append(instance.fxhigh)
            self.data_fxlow.append(instance.fxlow)
            self.data_timestamp.append(instance.timestamp)
            self.data_fxclose.append(instance.fxclose)
            self.data_fxvolume.append(instance.fxvolume)

    def timestamp(self):
        """Get timestamp data.

        Args:
            None

        Returns:
            value: List of timestamp data

        """
        # Return data
        value = self.data_timestamp
        return value

    def fxhigh(self):
        """Get fxhigh data.

        Args:
            None

        Returns:
            value: List of fxhigh data

        """
        # Return data
        value = self.data_fxhigh
        return value

    def fxlow(self):
        """Get fxlow data.

        Args:
            None

        Returns:
            value: List of fxlow data

        """
        # Return data
        value = self.data_fxlow
        return value

    def fxclose(self):
        """Get fxclose data.

        Args:
            None

        Returns:
            value: List of fxclose data

        """
        # Return data
        value = self.data_fxclose
        return value

    def fxvolume(self):
        """Get fxvolume data.

        Args:
            None

        Returns:
            value: List of fxvolume data

        """
        # Return data
        value = self.data_fxvolume
        return value
