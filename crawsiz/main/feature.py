"""Library to process the ingest of data files."""

# Standard imports
import time
import decimal
from random import randint
from collections import defaultdict

# Non standard imports
import numpy as np
from sqlalchemy import and_

# Import custom libraries
from crawsiz.utils import log
from crawsiz.db import db
from crawsiz.db import db_data
from crawsiz.db import db_pair
from crawsiz.db.db_orm import Prediction
from crawsiz.main import report
from crawsiz.machine import prediction
from crawsiz.utils import configuration


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
        intermediary = [-1]

        # # Classify
        # intermediary = [-1] * self.lookahead
        # for pointer in range(0, self.lookahead):
        #     if values[self.start + pointer + 1] > values[
        #             self.start + pointer]:
        #         intermediary[pointer] = 1

        # Classify
        if values[self.start + self.lookahead] > values[self.start]:
            intermediary = [1]

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

    def mean_volume_percent(self):
        """Calculate the mean of volumes as percent of current volume.

        Args:
            None

        Returns:
            result: Mean of volumes as percentage of current volume.

        """
        # Initialize key variables
        mean_value = sum(self._samples_volume()) / len(self._samples_volume())
        result = mean_value / self._current_volume()

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

    def _samples_volume(self):
        """Get samples of volumes to analyze.

        Args:
            None

        Returns:
            samples: Sample list

        """
        # Initialize key variables
        values = self.fxdata.fxvolume()
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

    def _current_volume(self):
        """Calculate the current volume.

        Args:
            None

        Returns:
            result: current volume

        """
        # Initialize key variables
        result = self._samples_volume()[-1]

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


class Extract(object):
    """Class to create feature vectors from database.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, idx_pair, lookahead=1, years=6):
        """Method for intializing the class.

        Args:
            idx_pair: FX cross
            lookahead: Number of periods to use for classification
            years: Years of data to retrieve

        Returns:
            None

        """
        # Initialize key variables
        self.kessler_classes_high = []
        self.kessler_classes_low = []
        self.regular_classes_high = []
        self.regular_classes_low = []
        self.feature_vectors = []
        self._timestamps = []
        self._idx_pair = idx_pair
        self._lookahead = lookahead

        # Get data object for
        self._fxdata = getdata(idx_pair, years=years)
        timestamps = self._fxdata.timestamp()

        # Create features
        for timestamp in timestamps[199:-lookahead]:
            # Append feature vector for this timestamp
            # to the list of feature vectors
            feature_vector = vector(self._fxdata, timestamp)
            self.feature_vectors.append(feature_vector)

            # Get classification for this timestamp
            classify = Classify(self._fxdata, timestamp, lookahead)
            self.kessler_classes_high.append(classify.high())
            self.kessler_classes_low.append(classify.low())
            self.regular_classes_high.append(classify.high(kessler=False))
            self.regular_classes_low.append(classify.low(kessler=False))

            # Append timestamp to array
            self._timestamps.append(timestamp)

    def fxdata(self):
        """Return fxdata.

        Args:
            None

        Returns:
            self._fxdata

        """
        # Return
        return self._fxdata

    def lookahead(self):
        """Return lookahead.

        Args:
            None

        Returns:
            self._lookahead

        """
        # Return
        return self._lookahead

    def idx_pair(self):
        """Return idx_pair.

        Args:
            None

        Returns:
            self._idx_pair

        """
        # Return
        return self._idx_pair

    def timestamps(self):
        """Return list of timestamps matching rows in self.feature_vectors.

        Args:
            None

        Returns:
            self._timestamps

        """
        # Return
        return self._timestamps

    def classes_high(self, kessler=False):
        """Method returning the high classifications of all feature vectors.

        Args:
            kessler: True if kesslerized results required

        Returns:
            data: One dimensional numpy array of classifications for each
                feature vector.

        """
        # Initialize key variables
        data = None

        # Return
        if kessler is True:
            data = np.asarray(self.kessler_classes_high)
        else:
            data = np.asarray(self.regular_classes_high)
        return data

    def classes_low(self, kessler=False):
        """Method returning the low classifications of all feature vectors.

        Args:
            kessler: True if kesslerized results required

        Returns:
            data: One dimensional numpy array of classifications for each
                feature vector.

        """
        # Initialize key variables
        data = None

        # Return
        if kessler is True:
            data = np.asarray(self.kessler_classes_low)
        else:
            data = np.asarray(self.regular_classes_low)
        return data

    def vectors(self):
        """Method returning all feature vectors up to fxdata[-lookahead].

        Args:
            None

        Returns:
            data: Numpy array of all feature vectors.

        """
        # Initialize key variables
        data = np.asarray(self.feature_vectors)

        # Return data
        return data

    def last_vector(self):
        """Method returning feature vector for fxdata[-1].

        Args:
            None

        Returns:
            data: Numpy array of all feature vectors.

        """
        # Initialize key variables
        data = vector(self._fxdata, self.last_timestamp())

        # Return data
        return data

    def last_timestamp(self):
        """Method returning timestamp for fxdata[-1].

        Args:
            None

        Returns:
            data: Numpy array of all feature vectors.

        """
        # Initialize key variables
        data = self._fxdata.timestamp()[-1]

        # Return data
        return data


def getdata(idx_pair, years=6):
    """Retrieve data from database.

    Args:
        idx_pair: FX cross
        years: Years of data to retrieve

    Returns:
        fxdata: Data object

    """
    # Initialize key variables
    seconds_in_year = 3600 * 24 * 365
    ts_stop = int(time.time())
    ts_start = ts_stop - (years * seconds_in_year)

    # Get data object for
    fxdata = db_data.GetIDX(idx_pair, ts_start, ts_stop)

    # Return
    return fxdata


def vector(fxdata, timestamp):
    """Create a feature vector.

    Args:
        fxdata: Object of fxdata table
        timestamp: Ending timestamp of data subset to be analyzed

    Returns:
        feature_vector: Feature vector

    """
    # Initialize key variables
    feature_vector = []

    # Start creating the vector
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

    # Return
    return feature_vector


def process(idx_pair, years=6, lookahead=1, components=10):
    """Process data.

    Args:
        idx_pair: Index of pair
        years: Number of years of data to process
        components: Number of principal components to analyze
        lookahead:

    Returns:
        None

    """
    # Initialize key variables
    data_dict = defaultdict(lambda: defaultdict(dict))

    # Sleep a random amount of time
    time.sleep(randint(0, 10))

    # Get pair as string
    cross_object = db_pair.GetIDX(idx_pair)
    cross = cross_object.pair().lower()

    # Log
    log_message = 'Starting to process {}.'.format(cross.upper())
    log.log2quiet(1001, log_message)

    # Get directory for web output
    config = configuration.Config()
    directory = config.web_directory()
    filepath = ('%s/%s.html') % (directory, cross)

    # Get data objects
    for next_lookahead in range(1, lookahead + 1):
        # Create extract object
        extract = Extract(
            idx_pair, lookahead=next_lookahead, years=years)

        # Get prediction data
        data_dict['predictions'][next_lookahead] = report.Data(
            extract, components=components).summary()

        # Get last_timestamp
        last_timestamp = extract.last_timestamp()

        # Update predictions in database
        _update_db_predictions(extract, components=components)

    # Add additional information to data_dict
    data_dict['years'] = years
    data_dict['idx_pair'] = idx_pair
    data_dict['lookahead'] = lookahead
    data_dict['last_timestamp'] = last_timestamp

    # Create a report object
    journal = report.Report(data_dict)

    # Create report
    html = journal.html()
    with open(filepath, 'w') as f_handle:
        f_handle.write(html)

    # Log
    log_message = 'Ended processing {}.'.format(cross.upper())
    log.log2quiet(1008, log_message)


def _update_db_predictions(extract, components=10):
    """Update database with predictions for current run.

    Args:
        extract: Extract object
        components: Number of principal components to analyze

    Returns:
        history: List of tuples

    """
    # Initialize key variables
    predictions = []
    lookahead = extract.lookahead()
    fxdata = extract.fxdata()
    idx_pair = extract.idx_pair()
    all_timestamps = sorted(extract.timestamps())
    timestamps = all_timestamps[-201: -1]

    # Delete all entries for this pair
    database = db.Database()
    session = database.session()
    session.query(Prediction).filter(
        and_(
            Prediction.idx_pair == idx_pair,
            Prediction.lookahead == lookahead)).delete(
                synchronize_session=False)
    session.commit()
    database.close()

    # Get predictions
    for timestamp in timestamps:
        feature_vector = vector(fxdata, timestamp)
        guess = prediction.BlackBox(extract, components=components)

        # Get predictions
        fxhigh_bayesian = guess.high(feature_vector, bayesian=True)
        fxlow_bayesian = guess.low(feature_vector, bayesian=True)
        fxhigh_linear = guess.high(feature_vector, bayesian=False)
        fxlow_linear = guess.low(feature_vector, bayesian=False)

        # Append predictions to history
        datapoint = Prediction(
            idx_pair=idx_pair,
            fxhigh_linear=int(fxhigh_linear),
            fxhigh_bayesian=int(fxhigh_bayesian),
            fxlow_linear=int(fxlow_linear),
            fxlow_bayesian=int(fxlow_bayesian),
            lookahead=lookahead,
            timestamp=timestamp
        )
        predictions.append(datapoint)

    # Update database
    database = db.Database()
    database.add_all(predictions, 9999)
