"""Module of crawsiz database functions.

Classes for agent data

"""
# Python standard libraries
from collections import defaultdict

# Python libraries
from sqlalchemy import and_

# Crawsiz libraries
from crawsiz.db import db
from crawsiz.db.db_orm import Prediction
from crawsiz.utils import log


class GetPrediction(object):
    """Class to return Prediction data by host and agent idx.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, idx_pair, timestamp):
        """Method initializing the class.

        Args:
            idx_pair: Pair idx
            timestamp: Timestamp of prediction

        Returns:
            None

        """
        # Initialize key variables
        self.data_dict = defaultdict(dict)

        # Establish a database session
        database = db.Database()
        session = database.session()
        result = session.query(Prediction).filter(and_(
            Prediction.idx_pair == idx_pair,
            Prediction.timestamp == timestamp))

        # Return the session to the database pool after processing
        session.close()

        # Massage data
        if result.count() == 1:
            for instance in result:
                self.data_dict['timestamp'] = instance.timestamp
                self.data_dict['fxhigh_bayesian'] = instance.fxhigh_bayesian
                self.data_dict['fxhigh_linear'] = instance.fxhigh_linear
                self.data_dict['fxlow_linear'] = instance.fxlow_linear
                self.data_dict['fxlow_bayesian'] = instance.fxlow_bayesian
                break
        else:
            log_message = (
                'Pair IDX %s timestamp %s not found in xs_prediction table.'
                '') % (idx_pair, timestamp)
            log.log2die(1105, log_message)

    def timestamp(self):
        """Get timestamp value.

        Args:
            None

        Returns:
            value: Value to return

        """
        # Initialize key variables
        value = self.data_dict['timestamp']
        return value

    def fxhigh_linear(self):
        """Get fxhigh_linear value.

        Args:
            None

        Returns:
            value: Value to return

        """
        # Initialize key variables
        value = self.data_dict['fxhigh_linear']
        return value

    def fxhigh_bayesian(self):
        """Get fxhigh_bayesian value.

        Args:
            None

        Returns:
            value: Value to return

        """
        # Initialize key variables
        value = self.data_dict['fxhigh_bayesian']
        return value

    def fxlow_linear(self):
        """Get fxlow_linear value.

        Args:
            None

        Returns:
            value: Value to return

        """
        # Initialize key variables
        value = self.data_dict['fxlow_linear']
        return value

    def fxlow_bayesian(self):
        """Get fxlow_bayesian value.

        Args:
            None

        Returns:
            value: Value to return

        """
        # Initialize key variables
        value = self.data_dict['fxlow_bayesian']
        return value


def prediction_exists(idx_pair, timestamp):
    """Determine whether an entry exists in the Prediction table.

    Args:
        idx_pair: Pair idx
        timestamp: Timestamp of prediction

    Returns:
        found: True if found

    """
    # Initialize key variables
    found = False

    # Establish a database session
    database = db.Database()
    session = database.session()
    result = session.query(Prediction.idx).filter(and_(
        Prediction.idx_pair == idx_pair,
        Prediction.timestamp == timestamp))

    # Massage data
    if result.count() == 1:
        for instance in result:
            _ = instance.idx
            break
        found = True

    # Return the session to the database pool after processing
    session.close()

    # Return
    return found
