"""Library to process the ingest of data files."""

from pprint import pprint
from sklearn.metrics import confusion_matrix
import numpy as np

# Import custom libraries
from crawsiz.machine import classifier
from crawsiz.machine import pca


class Linear(object):
    """Class to determine Linear prediction accuracy.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, extract):
        """Method for intializing the class.

        Args:
            extract: Extract object from feature module.

        Returns:
            None

        """
        # Apply classifer to all feature vectors
        feature_vectors = extract.vectors()
        linear = classifier.Linear(feature_vectors)

        # Assign values
        klasses_high = extract.classes_high(kessler=True)
        klasses_low = extract.classes_low(kessler=True)

        # Start predictions (high)
        predictions = []
        for feature_vector in feature_vectors:
            next_class = linear.classifier(feature_vector, klasses_high)
            predictions.append(next_class)
        predicted_high = np.asarray(predictions)

        # Start predictions (low)
        predictions = []
        for feature_vector in feature_vectors:
            next_class = linear.classifier(feature_vector, klasses_low)
            predictions.append(next_class)
        predicted_low = np.asarray(predictions)

        # Create confusion matrices
        self.matrix_high = confusion_matrix(klasses_high, predicted_high)
        self.matrix_low = confusion_matrix(klasses_low, predicted_low)

    def lowerhighs(self):
        """Accuracy of predicting a lower high.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.matrix_high[1, 1] / sum(self.matrix_high[:, -1])
        return accuracy

    def higherhighs(self):
        """Accuracy of predicting a higher high.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.matrix_high[0, 0] / sum(self.matrix_high[:, 0])
        return accuracy

    def highs(self):
        """Accuracy of predicting movement of highs.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = (self.matrix_high[0, 0] + self.matrix_high[1, 1]) / sum(
            sum(self.matrix_high))
        return accuracy

    def lowerlows(self):
        """Accuracy of predicting a lower high.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.matrix_low[1, 1] / sum(self.matrix_low[:, -1])
        return accuracy

    def higherlows(self):
        """Accuracy of predicting a higher high.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.matrix_low[0, 0] / sum(self.matrix_low[:, 0])
        return accuracy

    def lows(self):
        """Accuracy of predicting movement of lows.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = (self.matrix_low[0, 0] + self.matrix_low[1, 1]) / sum(
            sum(self.matrix_low))
        return accuracy


class Bayesian(object):
    """Class to determine Bayesian prediction accuracy.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, extract, components=2):
        """Method for intializing the class.

        Args:
            extract: Extract object from feature module.

        Returns:
            None

        """
        # Initialize key variables
        feature_vectors = extract.vectors()

        # Assign values
        klasses_high = extract.classes_high(kessler=True)
        klasses_low = extract.classes_low(kessler=True)

        # Apply classifer to all high feature vectors
        pca_highs = pca.PCA(feature_vectors, klasses_high)
        bayes_classifier = classifier.Bayesian(
            pca_highs, components=components)
        self.highs_accuracy = bayes_classifier.accuracy()

        # Apply classifer to all low feature vectors
        pca_lows = pca.PCA(feature_vectors, klasses_low)
        bayes_classifier = classifier.Bayesian(
            pca_lows, components=components)
        self.lows_accuracy = bayes_classifier.accuracy()

    def lowerhighs(self):
        """Accuracy of predicting a lower high.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.highs_accuracy[-1]
        return accuracy

    def higherhighs(self):
        """Accuracy of predicting a higher high.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.highs_accuracy[1]
        return accuracy

    def highs(self):
        """Accuracy of predicting movement of highs.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.highs_accuracy[None]
        return accuracy

    def lowerlows(self):
        """Accuracy of predicting a lower low.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.lows_accuracy[-1]
        return accuracy

    def higherlows(self):
        """Accuracy of predicting a higher low.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.lows_accuracy[1]
        return accuracy

    def lows(self):
        """Accuracy of predicting movement of lows.

        Args:
            None

        Returns:
            accuracy: Accuracy as a decimal value

        """
        accuracy = self.lows_accuracy[None]
        return accuracy
