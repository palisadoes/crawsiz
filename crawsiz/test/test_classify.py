#!/usr/bin/env python3
"""Test the classify module."""

import unittest
from mock import Mock

from crawsiz.main import classify as testimport


class GetIDX(object):
    """Class for db_data.GetIDX mock.

    A detailed tutorial about Python mocks can be found here:
    http://www.drdobbs.com/testing/using-mocks-in-python/240168251

    """

    def timestamp(self):
        """Get timestamp data."""
        pass

    def fxhigh(self):
        """Get fxhigh data."""
        pass

    def fxlow(self):
        """Get fxlow data."""
        pass

    def fxclose(self):
        """Get fxclose data."""
        pass

    def fxvolume(self):
        """Get fxvolume data."""


class KnownValues(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    # Create data for Mock
    seconds_in_day = 86400
    timestamps = list(range(0, seconds_in_day * 10, seconds_in_day))
    fxhigh = list(range(100, 0, -10))
    fxlow = list(range(60, 10, -5))
    fxclose = list(range(-22, -2, 2))

    # Instantiate the Mock
    fxdata = Mock(spec=GetIDX)
    mock_spec = {
        'fxhigh.return_value': fxhigh,
        'fxlow.return_value': fxlow,
        'fxclose.return_value': fxclose,
        'timestamp.return_value': timestamps
        }
    fxdata.configure_mock(**mock_spec)

    # Instantiate the test object
    timestamp = timestamps[-2]
    periods = 5
    testobj = testimport.Classify(fxdata, timestamp, periods)

    def test_max_high_percent(self):
        """Testing function max_high_percent."""
        # Define the expected
        max_high = max(self.testobj._samples_high())
        mean_high = self.testobj._mean_high()
        expected = max_high / mean_high

        # Compare with test results
        result = self.testobj.max_high_percent()
        self.assertEqual(result, expected)

    def test__start_stop(self):
        """Testing function _start_stop."""
        pass

    def test__samples_high(self):
        """Testing function _samples_high."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        expected = self.fxhigh[start: stop]

        # Compare with test results
        result = self.testobj._samples_high()
        self.assertEqual(result, expected)

    def test__samples_close(self):
        """Testing function _samples_close."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        expected = self.fxclose[start: stop]

        # Compare with test results
        result = self.testobj._samples_close()
        self.assertEqual(result, expected)

    def test__samples_low(self):
        """Testing function _samples_low."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        expected = self.fxlow[start: stop]

        # Compare with test results
        result = self.testobj._samples_low()
        self.assertEqual(result, expected)

    def test__mean_high(self):
        """Testing function _mean_high."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        highs = self.fxhigh[start: stop]
        expected = sum(highs) / len(highs)

        # Compare with test results
        result = self.testobj._mean_high()
        self.assertEqual(result, expected)

    def test__atr_high(self):
        """Testing function _atr_high."""
        pass

    def test__in_range(self):
        """Testing function _in_range."""
        pass


def _start_stop(timestamps, timestamp, periods):
    """Get start / stop indexes for class.

    Args:
        timestamps: List of timestamps
        timestamp: Timestamp at end of range
        periods: Length of expected list.

    Returns:
        (start, stop): Index of start and stop of sub list

    """
    # Get the index of the timestamp
    index = timestamps.index(timestamp) + 1

    # Get mean of list of last "periods" values
    start = index - periods
    stop = index

    # Return
    return (start, stop)


if __name__ == '__main__':

    # Do the unit test
    unittest.main()
