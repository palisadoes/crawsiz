"""Library to process the ingest of data files."""

# Standard imports
from collections import defaultdict

# Non standard imports

# Import custom libraries
from crawsiz.main import feature
from crawsiz.machine import accuracy
from crawsiz.machine import prediction
from crawsiz.utils import general
from crawsiz.db import db_pair


class Data(object):
    """Class to get report data."""

    def __init__(self, extract, components=10):
        """Method for intializing the class.

        Args:
            extract: Extract object
            years: Number of years of data to process

        Returns:
            None

        """
        # Initialize key variables
        self.extract = extract

        # Create linear accuracy object
        self._linear = accuracy.Linear(self.extract)

        # Create bayesian accuracy object
        self._bayesian = accuracy.Bayesian(
            self.extract, components=components)

        # Do prediction based on last entry in extract
        self.guess = prediction.Tomorrow(
            self.extract, components=components)

    def summary(self):
        """Create summary of predicted values.

        Args:
            None

        Returns:
            data_dict: Dict of formatted data

        """
        # Initialize key variables
        data_dict = defaultdict(lambda: defaultdict(dict))

        # Assign values
        data_dict['bayesian_high'] = self._bayesian_high()
        data_dict['bayesian_low'] = self._bayesian_low()
        data_dict['linear_high'] = self._linear_high()
        data_dict['linear_low'] = self._linear_low()

        # Return
        return data_dict

    def _format_data(self, guessed_class, guessed_accuracy):
        """Format data from predictions.

        Args:
            None

        Returns:
            data_dict: Dict of formatted data

        """
        # Initialize key variables
        data_dict = {
            'predicted_class': guessed_class,
            'accuracy': guessed_accuracy
        }

        # Return
        return data_dict

    def _bayesian_high(self):
        """Provide report on bayesian high predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Initialize key variables
        guessed_accuracy = None

        # Process highs
        guessed_class = self.guess.high(bayesian=True)

        # Print prediction
        if guessed_class == -1:
            guessed_accuracy = self._bayesian.lowerhighs() * 100
        else:
            guessed_accuracy = self._bayesian.higherhighs() * 100

        # Return
        output = self._format_data(guessed_class, guessed_accuracy)
        return output

    def _bayesian_low(self):
        """Provide report on bayesian low predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Initialize key variables
        guessed_accuracy = None

        # Process lows
        guessed_class = self.guess.low(bayesian=True)

        # Print prediction
        if guessed_class == -1:
            guessed_accuracy = self._bayesian.lowerlows() * 100
        else:
            guessed_accuracy = self._bayesian.lowerlows() * 100

        # Return
        output = self._format_data(guessed_class, guessed_accuracy)
        return output

    def _linear_high(self):
        """Provide report on linear high predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Process highs
        guessed_class = self.guess.high(bayesian=False)

        # Print prediction
        if guessed_class == -1:
            guessed_accuracy = self._linear.lowerhighs() * 100
        else:
            guessed_accuracy = self._linear.higherhighs() * 100

        # Return
        output = self._format_data(guessed_class, guessed_accuracy)
        return output

    def _linear_low(self):
        """Provide report on linear low predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Process lows
        guessed_class = self.guess.low(bayesian=False)

        # Print prediction
        if guessed_class == -1:
            guessed_accuracy = self._linear.lowerlows() * 100
        else:
            guessed_accuracy = self._linear.lowerlows() * 100

        # Return
        output = self._format_data(guessed_class, guessed_accuracy)
        return output


class Report(object):
    """Class to create reports."""

    def __init__(self, data):
        """Method for intializing the class.

        Args:
            data: Dict of data to use in report

        Returns:
            None

        """
        # Initialize key variables
        self.data = data
        idx_pair = data['idx_pair']
        years = data['years']
        self._fxdata = feature.getdata(idx_pair, years=years)

        # Get pair as string
        cross = db_pair.GetIDX(idx_pair)
        self.pair = cross.pair().upper()

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
</html></body>
""") % (self.pair,
        self.pair,
        _text(self._summary()),
        _text(self._linear()),
        _text(self._bayesian()),
        self._historical_highs(),
        self._historical_lows())

        # Return
        return output

    def _bayesian(self):
        """Provide report on bayesian predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Initialize key variables
        predictions = self.data['predictions']
        rows = []

        # Create headings
        heading = (
            'Day', 'Date', 'High', 'High Accuracy', 'Low', 'Low Accuracy')

        # Get data
        for next_lookahead, data_dict in sorted(predictions.items()):
            # Create symbols for table
            if data_dict['bayesian_high']['predicted_class'] > 0:
                high_direction = '^'
            else:
                high_direction = 'v'
            if data_dict['bayesian_low']['predicted_class'] > 0:
                low_direction = '^'
            else:
                low_direction = 'v'
            rows.append((
                next_lookahead,
                self._lookahead_date(next_lookahead),
                high_direction,
                '{:1.2f}%'.format(data_dict['bayesian_high']['accuracy']),
                low_direction,
                '{:1.2f}%'.format(data_dict['bayesian_low']['accuracy'])
            ))

        # Create table, return html
        table = _html_table(heading, rows)
        html = ('<h2>Bayesian Prediction</h2>\n%s') % (table)
        return html

    def _linear(self):
        """Provide report on linear predictions.

        Args:
            None

        Returns:
            output: Performance report

        """
        # Initialize key variables
        predictions = self.data['predictions']
        rows = []

        # Create headings
        heading = (
            'Day', 'Date', 'High', 'High Accuracy', 'Low', 'Low Accuracy')

        # Get data
        for next_lookahead, data_dict in sorted(predictions.items()):
            # Create symbols for table
            if data_dict['linear_high']['predicted_class'] > 0:
                high_direction = '^'
            else:
                high_direction = 'v'
            if data_dict['linear_low']['predicted_class'] > 0:
                low_direction = '^'
            else:
                low_direction = 'v'
            rows.append((
                next_lookahead,
                self._lookahead_date(next_lookahead),
                high_direction,
                '{:1.2f}%'.format(data_dict['linear_high']['accuracy']),
                low_direction,
                '{:1.2f}%'.format(data_dict['linear_low']['accuracy'])
            ))

        # Create table, return html
        table = _html_table(heading, rows)
        html = ('<h2>Linear Prediction</h2>\n%s') % (table)
        return html

    def _lookahead_date(self, lookahead):
        """Get date of lookahead.

        Args:
            lookahead: Lookahead in days

        Returns:
            date_of_prediction: Date of lookahead

        """
        # Initialize key varialbes
        last_timestamp = self.data['last_timestamp']
        prediction_seconds = 1440 * 60 * lookahead
        date_of_prediction = general.utc_timestring(
            last_timestamp + prediction_seconds)

        # Return
        return date_of_prediction

    def _summary(self):
        """Provide summary header for the report.

        Args:
            None

        Returns:
            output: Report header

        """
        # Initialize key varialbes
        last_timestamp = self.data['last_timestamp']
        last_data_date = general.utc_timestring(last_timestamp)

        # Create output
        output = ("""\
Last Date Processed: %s


""") % (last_data_date)

        # Return
        return output

    def _historical_highs(self):
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
        high_list = self._fxdata.fxhigh()
        timestamps = self._fxdata.timestamp()

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

    def _historical_lows(self):
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
        low_list = self._fxdata.fxlow()
        timestamps = self._fxdata.timestamp()

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
