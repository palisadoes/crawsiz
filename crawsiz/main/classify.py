"""Library to process the ingest of data files."""

import decimal

__author__ = 'Peter Harrison (Colovore LLC.) <peter@colovore.com>'
__version__ = '0.0.1'


class Classify(object):
    """Class ingests file data to update the database.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, fxdata, timestamp, periods):
        """Function for intializing the class.

        Args:
            fxdata: Object of fxdata table
            timestamp: Ending timestamp of data subset to be analyzed
            periods: Number of periods before timestamp to analyze

        Returns:
            None

        """
        # Initialize key variables
        self.fxdata = fxdata
        self.timestamp = timestamp
        self.periods = periods

    def max_high_percent(self):
        """Calculate the max high as percent of current high.

        Args:
            None

        Returns:
            result: Max high as percentage of current high.

        """
        # Initialize key variables
        result = self._max_high() / self._current_high()

        # Return
        return result

    def min_low_percent(self):
        """Calculate the min low as percent of current low.

        Args:
            None

        Returns:
            result: min low as percentage of current low.

        """
        # Initialize key variables
        result = self._min_low() / self._current_low()

        # Return
        return result

    def _start_stop(self):
        """Get start / stop indexes for class.

        Args:
            None

        Returns:
            samples: Sample list

        """
        # Get list of timestamps
        timestamps = self.fxdata.timestamp()

        # Get the index of the timestamp
        index = timestamps.index(self.timestamp) + 1

        # Get mean of list of last "periods" values
        start = index - self.periods
        stop = index

        # Return
        return (start, stop)

    def _samples_high(self):
        """Get samples of highs to analyze.

        Args:
            None

        Returns:
            samples: Sample list

        """
        # Initialize key variables
        values = self.fxdata.fxhigh()
        (start, stop) = self._start_stop()
        samples = values[start: stop]

        # Return
        return samples

    def _samples_close(self):
        """Get samples of close to analyze.

        Args:
            None

        Returns:
            samples: Sample list

        """
        # Initialize key variables
        values = self.fxdata.fxclose()
        (start, stop) = self._start_stop()
        samples = values[start: stop]

        # Return
        return samples

    def _samples_low(self):
        """Get samples of low to analyze.

        Args:
            None

        Returns:
            samples: Sample list

        """
        # Initialize key variables
        values = self.fxdata.fxlow()
        (start, stop) = self._start_stop()
        samples = values[start: stop]

        # Return
        return samples

    def _max_high(self):
        """Calculate the max of highs.

        Args:
            None

        Returns:
            result: max of highs

        """
        # Initialize key variables
        result = max(self._samples_high())

        # Return
        return result

    def _min_low(self):
        """Calculate the min of lows.

        Args:
            None

        Returns:
            result: min of lows

        """
        # Initialize key variables
        result = min(self._samples_low())

        # Return
        return result

    def _current_high(self):
        """Calculate the current high.

        Args:
            None

        Returns:
            result: current high

        """
        # Initialize key variables
        result = self._samples_high()[-1]

        # Return
        return result

    def _current_low(self):
        """Calculate the current low.

        Args:
            None

        Returns:
            result: current low

        """
        # Initialize key variables
        result = self._samples_low()[-1]

        # Return
        return result

    def _mean_high(self):
        """Calculate the mean of highs.

        Args:
            None

        Returns:
            result: mean of highs

        """
        # Initialize key variables
        result = sum(self._samples_high()) / len(self._samples_high())

        # Return
        return result

    def _atr(self):
        """Calculate the average true range.

        Args:
            None

        Returns:
            result: Average true range.

        """
        # Initialize key variables
        true_range = []
        fx_high = self._samples_high()
        fx_low = self._samples_low()
        fx_close = self._samples_close()

        # Calculate the true range
        for index in range(1, len(fx_high)):
            true_range.append(
                max(
                    fx_high[index] - fx_low[index],
                    abs(fx_high[index] - fx_close[index - 1]),
                    abs(fx_low[index] - fx_close[index - 1])
                    )
                )

        # Calculate the average true range
        result = sum(true_range) / len(true_range)

        # Return
        return result

    def max_atr_percent(self):
        """Max high as percent of delta between current high + atr.

        Args:
            None

        Returns:
            result: Delta between max high and (current high + atr )

        """
        # Initialize key variables
        current_high = self._current_high()
        max_high = self._max_high()
        atr = self._atr()

        # Calculate the metric
        metric = max_high - (current_high + atr)
        result = metric / current_high

        # Return
        return result

    def min_atr_percent(self):
        """Min low as percent of delta between current low - atr.

        Args:
            None

        Returns:
            result: Delta between min low and (current low - atr )

        """
        # Initialize key variables
        current_low = self._current_low()
        min_low = self._min_low()
        atr = self._atr()

        # Calculate the metric
        metric = min_low - (current_low - atr)
        result = metric / current_low

        # Return
        return result

    def min_psycho(self):
        """TBD.

        Args:
            None

        Returns:
            result: List of psychological lows as percentage of current low

        """
        # Initialize key variables
        lows = []
        formatter = '10000.'
        current_low = decimal.Decimal(self._current_low())

        # Create list of minumum psychological numbers
        for _ in range(0, 5):
            formatter = ('%s0') % (formatter)
            lows.append(
                float(current_low.quantize(
                    decimal.Decimal(formatter),
                    rounding=decimal.ROUND_DOWN)) / self._current_low()
            )

        # Return
        return lows

    def max_psycho(self):
        """TBD.

        Args:
            None

        Returns:
            result: List of psychological highs as percentage of current high

        """
        # Initialize key variables
        highs = []
        formatter = '10000.'
        current_high = decimal.Decimal(self._current_high())

        # Create list of maxumum psychological numbers
        for _ in range(0, 5):
            formatter = ('%s0') % (formatter)
            highs.append(
                float(current_high.quantize(
                    decimal.Decimal(formatter),
                    rounding=decimal.ROUND_DOWN)) / self._current_high()
            )

        # Return
        return highs
