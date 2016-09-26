#!/usr/bin/env python3
"""Nagios check general library."""

import sys
import datetime
import time
import getpass
import logging
import threading
import traceback


# Infoset libraries
from crawsiz.utils import configuration

# Define global variable
LOGGER = {}


class GetLog(object):
    """Class to manage the logging without duplicates."""

    def __init__(self):
        """Method initializing the class."""
        # Define key variables
        app_name = 'crawsiz'

        # Get the logging directory
        config = configuration.Config()
        log_file = config.log_file()

        # create logger with 'slurpy'
        self.logger_file = logging.getLogger(('%s_file') % (app_name))
        self.logger_stdout = logging.getLogger(('%s_console') % (app_name))

        # Set logging levels to file and stdout
        self.logger_stdout.setLevel(logging.DEBUG)
        self.logger_file.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)

        # add the handlers to the logger
        self.logger_file.addHandler(file_handler)
        self.logger_stdout.addHandler(stdout_handler)

    def logfile(self):
        """Return logger for file IO.

        Args:
            None

        Returns:
            value: Value of logger

        """
        # Return
        value = self.logger_file
        return value

    def stdout(self):
        """Return logger for terminal IO.

        Args:
            None

        Returns:
            value: Value of logger

        """
        # Return
        value = self.logger_stdout
        return value


class LogThread(threading.Thread):
    """LogThread should always be used in preference to threading.Thread.

    The interface provided by LogThread is identical to that of threading.
    Thread, however, if an exception occurs in the thread the error will be
    logged (using logging.exception) rather than printed to stderr.

    This is important in daemon style applications where stderr is redirected
    to /dev/null.

    """

    def __init__(self, **kwargs):
        """Method initializing the class.

        Args:
            None

        Returns:
            None

        """
        # Run stuff
        super().__init__(**kwargs)
        self._real_run = self.run
        self.run = self._wrap_run

    def _wrap_run(self):
        try:
            self._real_run()
        except:
            # logging.exception('Exception during LogThread.run')
            log2warn(1101, ('%s\n%s\n%s\n%s') % (
                sys.exc_info()[0],
                sys.exc_info()[1],
                sys.exc_info()[2],
                traceback.print_exc()))


def log2die_safe(code, message):
    """Log message to STDOUT only and die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Initialize key variables
    output = _message(code, message, True)
    print(output)
    sys.exit(2)


def log2warn(code, message):
    """Log warning message to file only, but don't die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Initialize key variables
    warning = ('WARNING - %s') % (message)
    _logit(code, warning, error=False, verbose=False)


def log2quiet(code, message):
    """Log status message to file only, but don't die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Log to screen and file
    _logit(code, message, error=False, verbose=False)


def log2see(code, message):
    """Log message to file and STDOUT, but don't die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Log to screen and file
    _logit(code, message, error=False)


def log2die(code, message):
    """Log to STDOUT and file, then die.

    Args:
        code: Error number
        message: Descriptive error string

    Returns:
        None
    """
    _logit(code, message, error=True)


def _logit(error_num, error_string, error=False, verbose=False):
    """Log slurpy errors to file and STDOUT.

    Args:
        error_num: Error number
        error_string: Descriptive error string
        error: Is this an error or not?
        verbose: If True print non errors to STDOUT

    Returns:
        None

    """
    # Define key variables
    global LOGGER
    username = getpass.getuser()

    # Create logger if it doesn't already exist
    if bool(LOGGER) is False:
        LOGGER = GetLog()
    logger_file = LOGGER.logfile()
    logger_stdout = LOGGER.stdout()

    # Log the message
    if error:
        log_message = (
            'ERROR [%s] (%sE): %s') % (
                username, error_num, error_string)
        logger_stdout.debug('%s', log_message)
        logger_file.debug(log_message)

        # All done
        sys.exit(2)
    else:
        log_message = (
            'STATUS [%s] (%sS): %s') % (
                username, error_num, error_string)
        logger_file.debug(log_message)
        if verbose:
            logger_stdout.debug('%s', log_message)


def _message(code, message, error=True):
    """Create a formatted message string.

    Args:
        code: Message code
        message: Message text
        error: If True, create a different message string

    Returns:
        output: Message result

    """
    # Initialize key variables
    time_object = datetime.datetime.fromtimestamp(time.time())
    timestring = time_object.strftime('%Y-%m-%d %H:%M:%S,%f')
    username = getpass.getuser()

    # Format string for error message, print and die
    if error is True:
        prefix = 'ERROR'
    else:
        prefix = 'STATUS'
    output = ('%s - %s - %s - [%s] %s') % (
        timestring, username, prefix, code, message)

    # Return
    return output
