#!/usr/bin/env python3
"""Test the classify module."""

import unittest
import random
import decimal

from mock import Mock

from crawsiz.main import feature as testimport


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
    total_periods = 100
    timestamps = list(
        range(0, seconds_in_day * total_periods, seconds_in_day))
    starter_list = random.sample(range(1, 1000), total_periods)
    fxhigh = [13 / value for value in starter_list]
    fxlow = [7 / value for value in starter_list]
    fxclose = [11 / value for value in starter_list]

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
    timestamp = timestamps[-10]
    periods = total_periods - 20
    testobj = testimport.Feature(fxdata, timestamp, periods)

    def test_high_class(self):
        """Testing function high_class."""
        # Define the expected
        (_, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        reference = self.fxlow[stop + 1]

        # Classify
        if reference > self.testobj._samples_high()[-1]:
            expected = 'Higher High'
        else:
            expected = 'Lower High'

        # Compare with test results
        result = self.testobj.high_class()
        self.assertEqual(result, expected)

    def test_low_class(self):
        """Testing function low_class."""
        # Define the expected
        (_, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        reference = self.fxlow[stop + 1]

        # Classify
        if reference > self.testobj._samples_low()[-1]:
            expected = 'Higher Low'
        else:
            expected = 'Lower Low'

        # Compare with test results
        result = self.testobj.low_class()
        self.assertEqual(result, expected)

    def test_max_high_percent(self):
        """Testing function max_high_percent."""
        # Define the expected
        max_high = max(self.testobj._samples_high())
        current_high = self.testobj._samples_high()[-1]
        expected = max_high / current_high

        # Compare with test results
        result = self.testobj.max_high_percent()
        self.assertEqual(result, expected)

    def test_min_low_percent(self):
        """Testing function min_low_percent."""
        # Define the expected
        min_low = min(self.testobj._samples_low())
        current_low = self.testobj._samples_low()[-1]
        expected = min_low / current_low

        # Compare with test results
        result = self.testobj.min_low_percent()
        self.assertEqual(result, expected)

    def test_mean_high_percent(self):
        """Testing function min_low_percent."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        highs = self.fxhigh[start: stop]
        mean_value = sum(highs) / len(highs)
        expected = mean_value / highs[-1]

        # Compare with test results
        result = self.testobj.mean_high_percent()
        self.assertEqual(result, expected)

    def test__start_stop(self):
        """Testing function _start_stop."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        lows = self.fxlow[start: stop]
        mean_value = sum(lows) / len(lows)
        expected = mean_value / lows[-1]

        # Compare with test results
        result = self.testobj.mean_low_percent()
        self.assertEqual(result, expected)

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

    def test__current_high(self):
        """Testing function _current_high."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        highs = self.fxhigh[start: stop]
        expected = highs[-1]

        # Compare with test results
        result = self.testobj._current_high()
        self.assertEqual(result, expected)

    def test__current_low(self):
        """Testing function _current_low."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        lows = self.fxlow[start: stop]
        expected = lows[-1]

        # Compare with test results
        result = self.testobj._current_low()
        self.assertEqual(result, expected)

    def test__min_low(self):
        """Testing function _min_low."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        lows = self.fxlow[start: stop]
        expected = min(lows)

        # Compare with test results
        result = self.testobj._min_low()
        self.assertEqual(result, expected)

    def test__max_high(self):
        """Testing function _max_high."""
        # Define the expected
        (start, stop) = _start_stop(
            self.timestamps, self.timestamp, self.periods)
        highs = self.fxhigh[start: stop]
        expected = max(highs)

        # Compare with test results
        result = self.testobj._max_high()
        self.assertEqual(result, expected)

    def test__atr(self):
        """Testing function _atr."""
        pass

    def test_max_atr_percent(self):
        """Testing function max_atr_percent."""
        pass

    def test_min_atr_percent(self):
        """Testing function min_atr_percent."""
        pass

    def test_min_psycho(self):
        """Testing function min_psycho."""
        # Initialize key variables
        lows = []
        current_low = decimal.Decimal(self.testobj._current_low())
        formatter = '10000.'

        # Create list of minumum psychological numbers
        for _ in range(0, 5):
            formatter = ('%s0') % (formatter)
            lows.append(
                float(current_low.quantize(
                    decimal.Decimal(formatter),
                    rounding=decimal.ROUND_DOWN)) / float(current_low)
            )

        # Test
        result = self.testobj.min_psycho()
        for idx, expected in enumerate(lows):
            self.assertEqual(result[idx], expected)

    def test_max_psycho(self):
        """Testing function max_psycho."""
        # Initialize key variables
        highs = []
        current_high = decimal.Decimal(self.testobj._current_high())
        formatter = '10000.'

        # Create list of maxumum psychological numbers
        for _ in range(0, 5):
            formatter = ('%s0') % (formatter)
            highs.append(
                float(current_high.quantize(
                    decimal.Decimal(formatter),
                    rounding=decimal.ROUND_UP)) / float(current_high)
            )

        # Test
        result = self.testobj.max_psycho()
        for idx, expected in enumerate(highs):
            self.assertEqual(result[idx], expected)


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
