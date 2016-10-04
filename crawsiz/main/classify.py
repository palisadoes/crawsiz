"""Library to process the ingest of data files."""


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
        """Calculate the max high as percent of mean.

        Args:
            None

        Returns:
            result: Max high as percentage of mean.

        """
        # Initialize key variables
        mean_high = self._mean_high()
        max_high = max(self._samples_high())

        # Get mean of list of last "periods" values
        result = max_high / mean_high

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

    def _atr_high(self):
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

    def _in_range(self):
        """TBD.

        Args:
            None

        Returns:
            result: TBD.

        """
        # Initialize key variables
        fx_high = self._samples_high()[-1]
        fx_close = self._samples_close()[-1]
        atr = self._atr_high()

        # Calculate the metric
        metric = fx_high - (fx_close + atr)
        result = metric / self._mean_high()

        # Return
        return result
