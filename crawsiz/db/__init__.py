#!/usr/bin/env python3
"""Infoset ORM classes.

Manages connection pooling among other things.

"""

# Main python libraries
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import event
from sqlalchemy import exc

# Infoset libraries
from crawsiz.utils import configuration
from crawsiz.db import db_orm
from crawsiz.utils import log

#############################################################################
# Setup a global pool for database connections
#############################################################################
POOL = None
DBURL = None


def main():
    """Process agent data.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    use_mysql = True
    pool_size = 50
    max_overflow = 50
    global POOL
    global DBURL

    # Get configuration
    config = configuration.Config()

    # Create DB connection pool
    if use_mysql is True:
        DBURL = ('mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4') % (
            config.db_username(), config.db_password(),
            config.db_hostname(), config.db_name())

        # Add MySQL to the pool
        db_engine = create_engine(
            DBURL, echo=False,
            encoding='utf8',
            max_overflow=max_overflow,
            pool_size=pool_size, pool_recycle=3600)

        # Fix for multiprocessing
        _add_engine_pidguard(db_engine)

        POOL = scoped_session(
            sessionmaker(
                autoflush=True,
                autocommit=False,
                bind=db_engine
            ))

    else:
        POOL = None


def _add_engine_pidguard(engine):
    """Add multiprocessing guards.

    Forces a connection to be reconnected if it is detected
    as having been shared to a sub-process.

    source
    ------

    http://docs.sqlalchemy.org/en/latest/faq/connections.html
    "How do I use engines / connections / sessions with
    Python multiprocessing, or os.fork()?"

    Args:
        engine: SQLalchemy engine instance

    Returns:
        None

    """
    @event.listens_for(engine, 'connect')
    def connect(dbapi_connection, connection_record):
        """Get the PID of the sub-process for connections.

        Args:
            dbapi_connection: Connection object
            connection_record: Connection record object

        Returns:
            None

        """
        connection_record.info['pid'] = os.getpid()

    @event.listens_for(engine, 'checkout')
    def checkout(dbapi_connection, connection_record, connection_proxy):
        """Checkout sub-processes connection for sub-processing if needed.

            Checkout is called when a connection is retrieved from the Pool.

        Args:
            dbapi_connection: Connection object
            connection_record: Connection record object
            connection_proxy: Connection proxy object

        Returns:
            None

        """
        # Get PID of main process
        pid = os.getpid()

        # Detect if this is a sub-process
        if connection_record.info['pid'] != pid:
            # substitute log.debug() or similar here as desired
            log_message = (
                'Parent process %s forked (%s) with an open '
                'database connection, '
                'which is being discarded and recreated.'
                '') % (
                    connection_record.info['pid'], pid)
            log.log2quiet(1079, log_message)

            connection_record.connection = connection_proxy.connection = None
            raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
            )


if __name__ == 'crawsiz.db':
    main()
