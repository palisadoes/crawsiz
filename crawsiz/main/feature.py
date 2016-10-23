"""Library to process the ingest of data files."""

import sys
import time
import decimal
from pprint import pprint

from sklearn.metrics import confusion_matrix
import numpy as np

# Import custom libraries
from crawsiz.db import db_data
from crawsiz.machine.linear import Linear

__author__ = 'Peter Harrison (Colovore LLC.) <peter@colovore.com>'
__version__ = '0.0.1'


class Classify(object):
    """Class to classify database data.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, fxdata, timestamp, lookahead):
        """Method for intializing the class.

        Args:
            fxdata: Object of fxdata table
            timestamp: Ending timestamp of data subset to be analyzed
            lookahead: Number of periods before timestamp to analyze

        Returns:
            None

        """
        # Initialize key variables
        self.fxdata = fxdata
        self.lookahead = lookahead

        # Get list of timestamps
        timestamps = self.fxdata.timestamp()

        # Get the index of the timestamp
        self.start = timestamps.index(timestamp)

    def low(self, kessler=True):
        """Kessler classification of the low data for timestamp.

        Args:
            kessler: True if kesslerized results required

        Returns:
            result: Kessler classification of the current state

        """
        # Initialize key variables
        values = self.fxdata.fxlow()

        # Classify
        result = self._classify(values, kessler=kessler)
        return result

    def high(self, kessler=True):
        """Kessler classification of the high data for timestamp.

        Args:
            kessler: True if kesslerized results required

        Returns:
            result: Kessler classification of the current state

        """
        # Initialize key variables
        values = self.fxdata.fxhigh()

        # Classify
        result = self._classify(values, kessler=kessler)
        return result

    def _classify(self, values, kessler):
        """Kessler classification of the data for timestamp.

        Args:
            values: Values to classify
            kessler: True if kesslerized results required

        Returns:
            result: Kessler classification of the data

        """
        # Initialize key variables
        intermediary = [-1] * self.lookahead

        # Classify
        for pointer in range(0, self.lookahead):
            if values[self.start + pointer + 1] > values[
                    self.start + pointer]:
                intermediary[pointer] = 1

        # Return
        if kessler is True:
            result = intermediary
        else:
            binary_list = [x if x == 1 else 0 for x in intermediary]
            binary_string = ''.join(str(x) for x in binary_list)
            decimal_value = int(binary_string, 2)
            result = decimal_value
        return result


class Feature(object):
    """Class to extract features from database.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, fxdata, timestamp, periods):
        """Method for intializing the class.

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

    def mean_high_percent(self):
        """Calculate the mean of highs as percent of current high.

        Args:
            None

        Returns:
            result: Mean of highs as percentage of current high.

        """
        # Initialize key variables
        mean_value = sum(self._samples_high()) / len(self._samples_high())
        result = mean_value / self._current_high()

        # Return
        return result

    def mean_low_percent(self):
        """Calculate the mean of lows as percent of current low.

        Args:
            None

        Returns:
            result: Mean of lows as percentage of current low.

        """
        # Initialize key variables
        mean_value = sum(self._samples_low()) / len(self._samples_low())
        result = mean_value / self._current_low()

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
                    rounding=decimal.ROUND_UP)) / self._current_high()
            )

        # Return
        return highs


def process(idx_pair, years=6):
    """Process data.

    Args:
        idx_pair: Index of pair
        years: Number of years of data to process

    Returns:
        None

    """
    # Initialize key variables
    lookahead = 1
    seconds_in_year = 3600 * 24 * 365
    klasses_high = []
    classes_low = []
    classes_high = []
    klasses_low = []
    feature_vectors = []
    ts_stop = int(time.time())
    ts_start = ts_stop - (years * seconds_in_year)

    # Get data object for
    fxdata = db_data.GetIDX(idx_pair, ts_start, ts_stop)
    timestamps = fxdata.timestamp()

    # Create features
    for timestamp in timestamps[199:-lookahead]:
        feature_vector = [0]
        for period in [20, 40, 60]:
            feature = Feature(fxdata, timestamp, period)

            # Append feature to feature_vector
            feature_vector.append(feature.max_high_percent())
            feature_vector.append(feature.min_low_percent())
            feature_vector.append(feature.mean_high_percent())
            feature_vector.append(feature.mean_low_percent())
            feature_vector.append(feature.max_atr_percent())
            feature_vector.append(feature.min_atr_percent())
            feature_vector.extend(feature.min_psycho())
            feature_vector.extend(feature.max_psycho())

        # Append for 200 moving average value
        feature = Feature(fxdata, timestamp, 200)
        feature_vector.append(feature.mean_high_percent())
        feature_vector.append(feature.mean_low_percent())

        # Get classification
        classify = Classify(fxdata, timestamp, lookahead)
        klasses_high.append(classify.high())
        klasses_low.append(classify.low())
        classes_high.append(classify.high(kessler=False))
        classes_low.append(classify.low(kessler=False))

        # Append feature vector to list of feature vectors
        feature_vectors.append(feature_vector)

        # Print
        # print(feature_vector, classify.low(), classify.high(), '\n')

    # Apply classifer
    linear = Linear(feature_vectors)
    # classifier_high = linear.classifier(klasses_high)
    # classifier_low = linear.classifier(klasses_low)

    np_classes_high = np.asarray(classes_high)
    np_classes_low = np.asarray(classes_low)
    np_klasses_high = np.asarray(klasses_high)
    np_klasses_low = np.asarray(klasses_low)
    np_feature_vectors = np.asarray(feature_vectors)

    # Start predictions (high)
    print('Predicting Highs')
    predicted_high = []
    for np_feature_vector in np_feature_vectors:
        next_class = linear.prediction(np_feature_vector, np_klasses_high)
        predicted_high.append(next_class)
    np_predicted_high = np.asarray(predicted_high)

    # Start predictions (low)
    print('Predicting Lows')
    predicted_low = []
    for np_feature_vector in np_feature_vectors:
        next_class = linear.prediction(np_feature_vector, np_klasses_low)
        predicted_low.append(next_class)
    np_predicted_low = np.asarray(predicted_low)

    # Confusion matrix
    print('Confusion Matrix Calculation')
    # print(type(np_klasses_high), np_klasses_high.shape, type(np_predicted_high), np_predicted_high.shape)
    # sys.exit(0)

    print(type(np_classes_high), np_classes_high.shape)
    print(type(np_klasses_high), np_klasses_high.shape)
    print(type(np_predicted_high), np_predicted_high.shape)
    #sys.exit(0)

    if lookahead > 1:
        matrix_high = confusion_matrix(np_classes_high, np_predicted_high)
        matrix_low = confusion_matrix(np_classes_low, np_predicted_low)
    else:
        matrix_high = confusion_matrix(np_klasses_high, np_predicted_high)
        matrix_low = confusion_matrix(np_klasses_low, np_predicted_low)

    pprint(matrix_high)

    pprint(matrix_low)
