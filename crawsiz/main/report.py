"""Library to process the ingest of data files."""

# Standard imports

# Non standard imports

# Import custom libraries
from crawsiz.machine import accuracy
from crawsiz.machine import prediction
from crawsiz.utils import configuration
from crawsiz.utils import general
from crawsiz.db import db
from crawsiz.db import db_pair
from crawsiz.db.db_orm import Prediction


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

    def __init__(self, extract, components=10):
        """Method for intializing the class.

        Args:
            extract: Extract object
            years: Number of years of data to process

        Returns:
            None

        """
        # Initialize key variables
        self.components = components
        self.extract = extract
        idx_pair = self.extract.idx_pair()
        config = configuration.Config()

        # Get timestamp of last entry
        timestamp = self.extract.last_timestamp()
        prediction_seconds = 1440 * 60 * config.lookahead()
        self.date = general.utc_timestring(timestamp)
        self.date_of_prediction = general.utc_timestring(
            timestamp + prediction_seconds)

        # Create linear accuracy object
        self._linear = accuracy.Linear(self.extract)

        # Create bayesian accuracy object
        self._bayesian = accuracy.Bayesian(
            self.extract, components=self.components)

        # Do prediction based on last entry in extract
        self.guess = prediction.Tomorrow(
            self.extract, components=self.components)

        # Get pair as string
        cross = db_pair.GetIDX(idx_pair)
        self.pair = cross.pair().upper()

    def summary(self):
        """Provide summary header for the report.

        Args:
            None

        Returns:
            output: Report header

        """
        # Create output
        output = ("""\
Prediction for Date: %s
Last Date Processed: %s


""") % (self.date_of_prediction, self.date)

        # Return
        return output

    def bayesian(self):
        """Provide report on bayesian predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Initialize key variables
        prefix = ("""\
Bayesian Prediction - %s
============================
""") % (self.pair)

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
Linear Prediction - %s
==========================
""") % (self.pair)

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

    def historical_highs(self):
        """Create table of historical highs.

        Args:
            None

        Returns:
            output: Historical report in HTML

        """
        # Initialize key variables
        values = ['Value']
        dates = ['Date']

        # Create headings
        heading = (
            '', '60 Day High', '120 Day High', '180 Day High', '240 Day High')

        # Get data from database
        high_list = self.extract.fxdata().fxhigh()
        timestamps = self.extract.fxdata().timestamp()

        # Get values
        for days in range(60, 241, 60):
            # Trim values to inspect
            value_list = high_list[-days - 1: -1]
            times_list = timestamps[-days - 1: -1]
            interesting_value = max(value_list)
            index = value_list.index(interesting_value)
            timestamp = times_list[index]
            date_string = general.utc_timestring(timestamp)

            # Append data
            values.append(interesting_value)
            dates.append(date_string)

        # Create report
        rows = [values, dates]
        table = _html_table(heading, rows)
        html = ('<h2>Historical Highs</h2>\n%s') % (table)

        # Return HTML
        return html

    def historical_lows(self):
        """Create table of historical lows.

        Args:
            None

        Returns:
            output: Historical report in HTML

        """
        # Initialize key variables
        values = ['Value']
        dates = ['Date']

        # Create headings
        heading = (
            '', '60 Day Low', '120 Day Low', '180 Day Low', '240 Day Low')

        # Get data from database
        low_list = self.extract.fxdata().fxlow()
        timestamps = self.extract.fxdata().timestamp()

        # Get values
        for days in range(60, 241, 60):
            # Trim values to inspect
            value_list = low_list[-days - 1: -1]
            times_list = timestamps[-days - 1: -1]
            interesting_value = min(value_list)
            index = value_list.index(interesting_value)
            timestamp = times_list[index]
            date_string = general.utc_timestring(timestamp)

            # Append data
            values.append(interesting_value)
            dates.append(date_string)

        # Create report
        rows = [values, dates]
        table = _html_table(heading, rows)
        html = ('<h2>Historical Lows</h2>\n%s') % (table)

        # Return HTML
        return html

    def historical_predictions(self):
        """Create table of historical predictions.

        Args:
            None

        Returns:
            output: Historical report in HTML

        """
        # Initialize key variables
        idx_pair = self.extract.idx_pair()
        rows = []

        # Create headings
        heading = (
            'Date',
            'Bayesian High',
            'Linear High',
            'Bayesian Low',
            'Linear Low'
        )

        # Get data from database
        database = db.Database()
        session = database.session()
        result = session.query(Prediction).filter(
            Prediction.idx_pair == idx_pair)
        database.close()

        # Process data
        for instance in result:
            timestamp = instance.timestamp

            # Create bayesian strings
            if instance.fxhigh_bayesian > 0:
                high_bayesian = "Higher High"
            else:
                high_bayesian = "Lower High"
            if instance.fxlow_bayesian > 0:
                low_bayesian = "Higher Low"
            else:
                low_bayesian = "Lower Low"

            # Create linear strings
            if instance.fxhigh_linear > 0:
                high_linear = "Higher High"
            else:
                high_linear = "Lower High"
            if instance.fxlow_linear > 0:
                low_linear = "Higher Low"
            else:
                low_linear = "Lower Low"

            # Create timestring
            timestring = general.utc_timestring(timestamp)

            # Create row for report
            row = (
                timestring,
                high_bayesian,
                high_linear,
                low_bayesian,
                low_linear
            )
            rows.append(row)

        # Create report
        table = _html_table(heading, sorted(rows, reverse=True))
        html = ('<h2>Historical Predictions</h2>\n%s') % (table)

        # Return HTML
        return html

    def html(self):
        """Provide report as HTML.

        Args:
            None

        Returns:
            output: Full report in HTML

        """
        # Initialize key variables
        output = ("""\
<html>
<head><title>%s</title></head>
<body>
<h1>%s</h1>
%s
%s
%s
%s
%s
%s
%s
</html></body>
""") % (self.pair,
        self.pair,
        _text(self.summary()),
        _text(self.linear()),
        _text(self.bayesian()),
        _text(self.performance()),
        self.historical_highs(),
        self.historical_lows(),
        self.historical_predictions())

        # Return
        return output


def _text(lines):
    """Convert text to text like HTML blocks.

    Args:
        None

    Returns:
        output: Full report in HTML

    """
    # Initialize key variables
    output = (
        '<p style="font-family:courier">%s</p>'
        '') % (lines.replace('\n', '<br>\n'))
    output = output.replace('  ', '&nbsp;&nbsp;')
    return output


def _html_table(heading, rows, highlight_duplicates=False):
    """Create HTML table.

    Args:
        heading: Headings as a tuple
        rows: List of tuples to be used as HTML row data
        highlight_duplicates: Highlight duplicates if found

    Returns:
        html: HTML

    """
    # Initialize key variables
    html = '<table cellpadding="7">'
    thstart = '<th bgcolor="#8CAA39"><font color="#FFFFFF">'
    td_e = '<td>'
    odd_row = True
    odd_color = '#EEEEFF'
    evn_color = '#B0E0E6'
    previous_value = None

    # Create header
    html = ('%s%s%s') % (
        html, thstart, (('</font></th>\n %s') % (thstart)).join(heading))
    html = ('%s</th>') % (html)

    # Loop through list
    for tuple_row in rows:
        # Convert tuple to a list of strings
        row = []
        for item in tuple_row:
            row.append(('%s') % (item))

        # Logic to alter colors
        current_value = row[0]
        if highlight_duplicates is True and current_value == previous_value:
            pass
        else:
            if odd_row is True:
                odd_row = False
                color = odd_color
            else:
                odd_row = True
                color = evn_color

        # Print entry row
        html = ('%s\n <tr bgcolor="%s">\n %s') % (html, color, td_e)
        html = ('%s%s') % (html, (('</td>%s') % (td_e)).join(row))
        html = ('%s\n  </td>\n </tr>') % (html)

        # Update previous value
        previous_value = current_value

    # Finish the table
    html = ('%s\n</table>\n') % (html)

    # Strip out any duplicated spaces
    html = ' '.join(html.split())

    # Strip out any duplicated line feeds
    html = '\n'.join(html.split('\n'))

    # Return
    return html
