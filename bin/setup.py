#!/usr/bin/env python3
"""Infoset ORM classes.

Manages connection pooling among other things.

"""

# Main python libraries
import sys

# Pip3 libraries
from sqlalchemy import create_engine

# Infoset libraries
try:
    from crawsiz.utils import log
except:
    print('You need to set your PYTHONPATH to include the crawsiz library')
    sys.exit(2)
from crawsiz.utils import configuration
from crawsiz.db.db_orm import BASE
from crawsiz.db import DBURL


def server_setup():
    """Setup server.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    use_mysql = True
    pool_size = 25
    max_overflow = 25

    # Get configuration
    config = configuration.Config()

    # Create DB connection pool
    if use_mysql is True:
        # Add MySQL to the pool
        engine = create_engine(
            DBURL, echo=True,
            encoding='utf8',
            max_overflow=max_overflow,
            pool_size=pool_size, pool_recycle=3600)

        # Try to create the database
        print('Attempting to create database tables')
        try:
            sql_string = (
                'ALTER DATABASE %s CHARACTER SET utf8mb4 '
                'COLLATE utf8mb4_general_ci') % (config.db_name())
            engine.execute(sql_string)
        except:
            log_message = (
                'Cannot connect to database %s. '
                'Verify database server is started. '
                'Verify database is created. '
                'Verify that the configured database authentication '
                'is correct.') % (config.db_name())
            log.log2die(1036, log_message)

        # Apply schemas
        print('Applying Schemas')
        BASE.metadata.create_all(engine)


def main():
    """Process agent data.

    Args:
        None

    Returns:
        None

    """
    # Run server setup if required
    server_setup()


if __name__ == '__main__':
    main()
