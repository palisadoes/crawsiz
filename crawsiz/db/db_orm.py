#!/usr/bin/env python3
"""Infoset ORM classes.

Manages connection pooling among other things.

"""

# SQLobject stuff
from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.dialects.mysql import FLOAT, VARBINARY
from sqlalchemy import Column
from sqlalchemy import ForeignKey

BASE = declarative_base()


class Data(BASE):
    """Class defining the crw_data table of the database."""

    __tablename__ = 'crw_data'
    __table_args__ = (
        PrimaryKeyConstraint(
            'idx_cross', 'timestamp'),
        {
            'mysql_engine': 'InnoDB'
        }
        )

    idx_cross = Column(
        BIGINT(unsigned=True), ForeignKey('crw_pair.idx'),
        nullable=False, server_default='1')

    fxopen = Column(FLOAT, default=None)

    fxhigh = Column(FLOAT, default=None)

    fxlow = Column(FLOAT, default=None)

    fxclose = Column(FLOAT, default=None)

    fxvolume = Column(FLOAT, default=None)

    timestamp = Column(BIGINT(unsigned=True), nullable=False, default='1')

    ts_modified = Column(
        DATETIME, server_default=text(
            'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),)

    ts_created = Column(
        DATETIME, server_default=text('CURRENT_TIMESTAMP'))


class Pair(BASE):
    """Class defining the crw_pair table of the database."""

    __tablename__ = 'crw_pair'
    __table_args__ = (
        UniqueConstraint(
            'pair'),
        {
            'mysql_engine': 'InnoDB'
        }
        )

    idx = Column(
        BIGINT(unsigned=True), primary_key=True,
        autoincrement=True, nullable=False)

    pair = Column(VARBINARY(512), nullable=True, default=None)

    ts_modified = Column(
        DATETIME, server_default=text(
            'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),)

    ts_created = Column(
        DATETIME, server_default=text('CURRENT_TIMESTAMP'))
