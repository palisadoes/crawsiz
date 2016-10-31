"""Library to process the ingest of data files."""

# Standard imports
from datetime import datetime

# Non standard imports

# Import custom libraries
from crawsiz.machine import accuracy
from crawsiz.machine import prediction
from crawsiz.main import feature
from crawsiz.db import db_pair


__author__ = 'Peter Harrison (Colovore LLC.) <peter@colovore.com>'
__version__ = '0.0.1'


class Report(object):
    """Class to classify database data.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, idx_pair, years=6, lookahead=1, components=10):
        """Method for intializing the class.

        Args:
            idx_pair: Index of pair
            years: Number of years of data to process

        Returns:
            None

        """
        # Get data object
        extract = feature.Extract(idx_pair, lookahead=lookahead, years=years)

        # Get timestamp of last entry
        timestamp = extract.timestamp()[-1]
        self.date = datetime.fromtimestamp(
            timestamp).strftime('%Y-%m-%d %H:%M')

        # Create linear accuracy object
        self._linear = accuracy.Linear(extract)

        # Create bayesian accuracy object
        self._bayesian = accuracy.Bayesian(extract, components=components)

        # Do prediction
        self.guess = prediction.Prediction(extract, components=components)

        # Get pair as string
        cross = db_pair.GetIDX(idx_pair)
        self.pair = cross.pair().upper()

    def bayesian(self):
        """Provide report on bayesian predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Initialize key variables
        prefix = ("""\
Bayesian Prediction - %s - %s
===============================================
""") % (self.pair, self.date)

        # Process highs
        guessed_class = self.guess.high(bayesian=True)

        # Print prediction
        if guessed_class == -1:
            high_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Lower high', self._bayesian.lowerhighs() * 100)
        else:
            high_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Higher high', self._bayesian.higherhighs() * 100)

        # Process lows
        guessed_class = self.guess.low(bayesian=True)

        # Print prediction
        if guessed_class == -1:
            low_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Lower low', self._bayesian.lowerlows() * 100)
        else:
            low_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Higher low', self._bayesian.higherlows() * 100)

        # Return
        output = ('\n%s\n%s\n%s') % (prefix, high_result, low_result)
        return output

    def linear(self):
        """Provide report on linear predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Initialize key variables
        prefix = ("""\
Linear Prediction - %s - %s
=============================================
""") % (self.pair, self.date)

        # Process highs
        guessed_class = self.guess.high(bayesian=False)

        # Print prediction
        if guessed_class == -1:
            high_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Lower high', self._linear.lowerhighs() * 100)
        else:
            high_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Higher high', self._linear.higherhighs() * 100)

        # Process lows
        guessed_class = self.guess.low(bayesian=False)

        # Print prediction
        if guessed_class == -1:
            low_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Lower low', self._linear.lowerlows() * 100)
        else:
            low_result = (
                '%-12s: %.2f%% probability'
                '') % (
                    'Higher low', self._linear.higherlows() * 100)

        # Return
        output = ('\n%s\n%s\n%s') % (prefix, high_result, low_result)
        return output

    def performance(self):
        """Provide performance data for the report.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Create linear results
        linear_output = ("""\
Linear Classifier Performance - %s
======================================

Higher High Predictive Value  : %.2f%%
Lower High Predictive Value   : %.2f%%
Overall High Predictive Value : %.2f%%

Higher Low Predictive Value   : %.2f%%
Lower Low Predictive Value    : %.2f%%
Overall Low Predictive Value  : %.2f%%\
""") % (self.pair,
        self._linear.higherhighs() * 100, self._linear.lowerhighs() * 100,
        self._linear.highs() * 100, self._linear.higherlows() * 100,
        self._linear.lowerlows() * 100, self._linear.lows() * 100)

        # Create bayesian results
        bayesian_output = ("""\
Bayesian Classifier Performance - %s
========================================

Higher High Predictive Value  : %.2f%%
Lower High Predictive Value   : %.2f%%
Overall High Predictive Value : %.2f%%

Higher Low Predictive Value   : %.2f%%
Lower Low Predictive Value    : %.2f%%
Overall Low Predictive Value  : %.2f%%\
""") % (self.pair,
        self._bayesian.higherhighs() * 100, self._bayesian.lowerhighs() * 100,
        self._bayesian.highs() * 100, self._bayesian.higherlows() * 100,
        self._bayesian.lowerlows() * 100, self._bayesian.lows() * 100)

        # Return
        output = ('\n%s\n\n%s') % (linear_output, bayesian_output)
        return output
