#!/usr/bin/env python3
"""crawsiz classes that manage various configurations."""

import os.path
import os

# Import project libraries
from crawsiz.utils import general
from crawsiz.utils import log


class Config(object):
    """Class gathers all configuration information.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        values:
        snmp_auth:
    """

    def __init__(self):
        """Function for intializing the class.

        Args:
            None

        Returns:
            None

        """
        # Update the configuration directory
        # 'INFOSET_CONFIGDIR' is used for unittesting
        if 'INFOSET_CONFIGDIR' in os.environ:
            config_directory = os.environ['INFOSET_CONFIGDIR']
        else:
            config_directory = ('%s/etc') % (general.root_directory())
        directories = [config_directory]

        # Return
        self.config_dict = general.read_yaml_files(directories)

    def pairs(self):
        """Get all pairs in the configuration file.

        Args:
            None

        Returns:
            result: List of pairs

        """
        # Initialize key variables
        result = None
        key = 'ingest'
        sub_key = 'pairs'

        # Process configuration
        values = _key_sub_key(key, sub_key, self.config_dict)
        if values is not None:
            if isinstance(values, list) is True:
                result = sorted(values)

        # Convert to upper case
        result = [x.upper() for x in result]

        # Return
        return result

    def valid_pair(self, pair=None):
        """Determine whether pair is valid.

        Args:
            pair: FX pair

        Returns:
            result: True if valid
        """
        # Intialize key variables
        result = False

        # Get symbols
        pairs = self.pairs()

        # Verify
        if pair in pairs:
            result = True

        # Return
        return result

    def timeframes(self):
        """Get all timeframes in the configuration file.

        Args:
            None

        Returns:
            result: List of timeframes

        """
        # Initialize key variables
        result = None
        key = 'ingest'
        sub_key = 'timeframes'

        # Process configuration
        values = _key_sub_key(key, sub_key, self.config_dict)
        if values is not None:
            if isinstance(values, list) is True:
                result = sorted(values)

        # Return
        return result

    def log_file(self):
        """Get log_file.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        sub_key = 'log_file'
        result = None
        key = 'general'

        # Get new result
        result = _key_sub_key(key, sub_key, self.config_dict)

        # Return
        return result

    def ingest_directory(self):
        """Determine the ingest_directory.

        Args:
            None

        Returns:
            value: configured ingest_directory

        """
        # Get parameter
        key = 'general'
        sub_key = 'ingest_directory'

        # Get result
        value = _key_sub_key(key, sub_key, self.config_dict)

        # Determine whether path exists
        if os.path.isdir(value) is False:
            log_message = (
                'ingest_directory: "%s" '
                'in configuration doesn\'t exist!') % (value)
            log.log2die(1007, log_message)

        # Return
        return value

    def archive_directory(self):
        """Determine the archive_directory.

        Args:
            None

        Returns:
            value: configured archive_directory

        """
        # Get parameter
        key = 'general'
        sub_key = 'archive_directory'

        # Get result
        value = _key_sub_key(key, sub_key, self.config_dict)

        # Determine whether path exists
        if os.path.isdir(value) is False:
            log_message = (
                'archive_directory: "%s" '
                'in configuration doesn\'t exist!') % (value)
            log.log2die(1007, log_message)

        # Return
        return value

    def web_directory(self):
        """Determine the web_directory.

        Args:
            None

        Returns:
            value: configured web_directory

        """
        # Get parameter
        key = 'general'
        sub_key = 'web_directory'

        # Get result
        value = _key_sub_key(key, sub_key, self.config_dict)

        # Determine whether path exists
        if os.path.isdir(value) is False:
            log_message = (
                'web_directory: "%s" '
                'in configuration doesn\'t exist!') % (value)
            log.log2die(1007, log_message)

        # Return
        return value

    def db_name(self):
        """Get db_name.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'database'
        sub_key = 'db_name'

        # Process configuration
        result = _key_sub_key(key, sub_key, self.config_dict)

        # Get result
        return result

    def db_username(self):
        """Get db_username.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'database'
        sub_key = 'db_username'

        # Process configuration
        result = _key_sub_key(key, sub_key, self.config_dict)

        # Get result
        return result

    def db_password(self):
        """Get db_password.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'database'
        sub_key = 'db_password'

        # Process configuration
        result = _key_sub_key(key, sub_key, self.config_dict)

        # Get result
        return result

    def db_hostname(self):
        """Get db_hostname.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'database'
        sub_key = 'db_hostname'

        # Process configuration
        result = _key_sub_key(key, sub_key, self.config_dict)

        # Get result
        return result


def _key_sub_key(key, sub_key, config_dict, die=True):
    """Get config parameter from YAML.

    Args:
        key: Primary key
        sub_key: Secondary key
        config_dict: Dictionary to explore
        die: Die if true and the result encountered is None

    Returns:
        result: result

    """
    # Get result
    result = None

    # Get new result
    if key in config_dict:
        if sub_key in config_dict[key]:
            result = config_dict[key][sub_key]

    # Error if not configured
    if result is None and die is True:
        log_message = (
            '%s:%s not defined in configuration') % (key, sub_key)
        log.log2die(1016, log_message)

    # Return
    return result
