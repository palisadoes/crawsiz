"""Module of crawsiz database functions.

Classes for agent data

"""
# Python standard libraries
from collections import defaultdict

# Infoset libraries
from crawsiz.utils import log
from crawsiz.utils import general
from crawsiz.db import db
from crawsiz.db.db_orm import Pair


class GetIDX(object):
    """Class to return agent data.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, idx_pair):
        """Function for intializing the class.

        Args:
            idx_pair: Pair idx

        Returns:
            None

        """
        # Initialize important variables
        self.data_dict = defaultdict(dict)

        # Get the result
        database = db.Database()
        session = database.session()
        result = session.query(Pair).filter(
            Pair.idx == idx_pair)

        # Massage data
        if result.count() == 1:
            for instance in result:
                self.data_dict['pair'] = general.decode(instance.pair)
                break
        else:
            log_message = ('Pair IDX %s not found.') % (idx_pair)
            log.log2die(1035, log_message)

        # Return the session to the database pool after processing
        session.close()

    def pair(self):
        """Get pair value.

        Args:
            None

        Returns:
            value: Value to return

        """
        # Initialize key variables
        value = self.data_dict['pair']
        return value


class GetPair(object):
    """Class to return agent data.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, pair):
        """Function for intializing the class.

        Args:
            pair: Pair of agent

        Returns:
            None

        """
        # Initialize important variables
        self.data_dict = defaultdict(dict)
        value = pair.encode()
        self.pair = value

        # Establish a database session
        database = db.Database()
        session = database.session()
        result = session.query(Pair).filter(Pair.pair == value)

        # Massage data
        if result.count() == 1:
            for instance in result:
                self.data_dict['idx'] = instance.idx
                break
        else:
            log_message = ('pair %s not found.') % (value)
            log.log2die(1042, log_message)

        # Return the session to the database pool after processing
        session.close()

    def idx(self):
        """Get idx value.

        Args:
            None

        Returns:
            value: Value to return

        """
        # Initialize key variables
        value = self.data_dict['idx']
        return value


def pair_exists(pair):
    """Determine whether the Pair exists.

    Args:
        pair: Pair value for agent

    Returns:
        found: True if found

    """
    # Initialize key variables
    found = False
    value = pair.encode()

    # Establish a database session
    database = db.Database()
    session = database.session()
    result = session.query(Pair.pair).filter(Pair.pair == value)

    # Massage data
    if result.count() == 1:
        for instance in result:
            _ = instance.pair
            break
        found = True

    # Return the session to the database pool after processing
    session.close()

    # Return
    return found


def idx_exists(idx):
    """Determine whether the idx exists.

    Args:
        idx: idx value for datapoint

    Returns:
        found: True if found

    """
    # Initialize key variables
    found = False

    # Establish a database session
    database = db.Database()
    session = database.session()
    result = session.query(Pair.idx).filter(Pair.idx == idx)

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
