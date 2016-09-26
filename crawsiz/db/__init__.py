#!/usr/bin/env python3
"""Infoset ORM classes.

Manages connection pooling among other things.

"""

# Main python libraries
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Infoset libraries
from crawsiz.utils import configuration
from crawsiz.db import db_orm

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
    pool_size = 25
    max_overflow = 25
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

        POOL = sessionmaker(
            autoflush=True,
            autocommit=False,
            bind=db_engine
        )

    else:
        POOL = None


if __name__ == 'crawsiz.db':
    main()
