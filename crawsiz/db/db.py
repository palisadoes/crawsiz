#!/usr/bin/env python3

"""Class to process connection."""

from sqlalchemy import and_

# Infoset libraries
from crawsiz.utils import log
from crawsiz.db import POOL
from crawsiz.db.db_orm import Pair


class Database(object):
    """Class interacts with the connection.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self):
        """Function for intializing the class.

        Args:
            config: Config object

        Returns:
            None

        """
        # Intialize key variables
        self.pool = POOL

    def query(self, sql_statement, error_code):
        """Do a database query.

        Args:
            sql_statement: SQL statement
            error_code: Error number to use if one occurs

        Returns:
            query_results: Query results

        """
        # Make sure this is a SELECT statement
        first_word = sql_statement.split()[0]
        if first_word.lower() != 'select':
            log_message = ('db_query function can only do SELECT: '
                           'SQL statement %s') % (sql_statement)
            log.log2die(error_code, log_message)

        # Open database connection. Prepare cursor
        session = self.session()

        try:
            # Execute the SQL command
            query_results = session.execute(sql_statement)

        except Exception as exception_error:
            log_message = (
                'Unable to fetch data from connection. '
                'SQL statement: \"%s\" Error: \"%s\"') % (
                    sql_statement, exception_error)
            log.log2die(error_code, log_message)
        except:
            log_message = ('Unexpected exception. SQL statement: \"%s\"') % (
                sql_statement)
            log.log2die(error_code, log_message)

        # Disconnect from server
        self.close()

        return query_results

    def modify(self, sql_statement, error_code):
        """Do a database modification.

        Args:
            sql_statement: SQL statement
            error_code: Error number to use if one occurs
            data_list: If not False, then the SQL statement is referring
                to a bulk update using a list of tuples contained in
                data_list.

        Returns:
            None

        """
        # Make sure this is a UPDATE, INSERT or REPLACE statement
        first_word = sql_statement.split()[0]
        if ((first_word.lower() != 'update') and
                (first_word.lower() != 'delete') and
                (first_word.lower() != 'insert') and
                (first_word.lower() != 'replace')):

            log_message = ('db_modify function can only do '
                           'INSERT, UPDATE, DELETE or REPLACE: '
                           'SQL statement %s') % (sql_statement)
            log.log2die(error_code, log_message)

        # Open database connection. Prepare cursor
        session = self.session()

        try:
            # Execute the SQL command
            session.execute(sql_statement)

            # Commit  change
            session.commit()

        except Exception as exception_error:
            session.rollback()
            log_message = (
                'Unable to modify connection. '
                'SQL statement: \"%s\" Error: \"%s\"') % (
                    sql_statement, exception_error)
            log.log2die(error_code, log_message)
        except:
            session.rollback()
            log_message = ('Unexpected exception. SQL statement: \"%s\"') % (
                sql_statement)
            log.log2die(error_code, log_message)

        # disconnect from server
        self.close()

    def add_all(self, data_list, error_code, die=True):
        """Do a database modification.

        Args:
            data_list: List of sqlalchemy table objects
            error_code: Error number to use if one occurs
            die: Don't die if False, just return success

        Returns:
            success: True is successful

        """
        # Initialize key variables
        success = False

        # Open database connection. Prepare cursor
        session = self.session()

        try:
            # Update the database cache
            session.add_all(data_list)

            # Commit  change
            session.commit()

            # Update success
            success = True

        except Exception as exception_error:
            success = False
            session.rollback()
            log_message = (
                'Unable to modify database connection. '
                'Error: \"%s\"') % (exception_error)
            if die is True:
                log.log2die(error_code, log_message)
            else:
                log.log2warn(error_code, log_message)

        except:
            success = False
            session.rollback()
            log_message = ('Unexpected database exception')
            if die is True:
                log.log2die(error_code, log_message)
            else:
                log.log2warn(error_code, log_message)

        # disconnect from server
        self.close()

        # Return
        return success

    def session(self):
        """Get a session from the database pool.

        Args:
            None

        Returns:
            db_session: Session

        """
        # Initialize key variables
        db_session = self.pool()
        return db_session

    def close(self):
        """Return a session to the database pool.

        Args:
            None

        Returns:
            None

        """
        # Return session
        self.pool.remove()

    def commit(self, session, error_code):
        """Do a database modification.

        Args:
            session: Session
            error_code: Error number to use if one occurs

        Returns:
            None

        """
        # Do commit
        try:
            # Commit  change
            session.commit()

        except Exception as exception_error:
            session.rollback()
            log_message = (
                'Unable to modify database connection. '
                'Error: \"%s\"') % (exception_error)
            log.log2die(error_code, log_message)
        except:
            session.rollback()
            log_message = ('Unexpected database exception')
            log.log2die(error_code, log_message)

        # disconnect from server
        self.close()

    def add(self, record, error_code):
        """Add a record to the database.

        Args:
            record: Record object
            error_code: Error number to use if one occurs

        Returns:
            None

        """
        # Initialize key variables
        session = self.session()

        # Do add
        try:
            # Commit change
            session.add(record)
            session.commit()

        except Exception as exception_error:
            session.rollback()
            log_message = (
                'Unable to modify database connection. '
                'Error: \"%s\"') % (exception_error)
            log.log2die(error_code, log_message)
        except:
            session.rollback()
            log_message = ('Unexpected database exception')
            log.log2die(error_code, log_message)

        # disconnect from server
        self.close()


def connectivity():
    """Check connectivity to the database.

    Args:
        None

    Returns:
        valid: True if connectivity is OK

    """
    # Initialize key variables
    valid = False

    # Do test
    session = Database().session()

    try:
        result = session.query(Pair.idx).filter(
            and_(Pair.pair == '-1'.encode(), Pair.idx == -1))
        for _ in result:
            break
        valid = True
    except:
        pass

    self.close()

    # Return
    return valid
