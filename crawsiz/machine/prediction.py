"""Library to process the ingest of data files."""

# Standard imports

# Non standard imports

# Import custom libraries
from crawsiz.machine import pca
from crawsiz.machine import classifier
from crawsiz.main import feature


__author__ = 'Peter Harrison (Colovore LLC.) <peter@colovore.com>'
__version__ = '0.0.1'


class Tomorrow(object):
    """Class to predict tomorrow's outcome.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, extract, components=10):
        """Method for intializing the class.

        Args:
            extract: feature.Extract object
            components: Number principal components to use

        Returns:
            None

        """
        # Initialize key variables
        self.components = components

        # Do prediction
        timestamps = extract.timestamps()
        fxdata = extract.fxdata()
        last_timestamp = timestamps[-1]

        # Create feature vector
        self.feature_vector = feature.vector(fxdata, last_timestamp)

        # Create prediction object
        self._prediction = BlackBox(extract, components=components)

    def high(self, bayesian=True):
        """Provide prediction of a high.

        Args:
            bayesian:
                True if bayesian classifier to be used
                False if linear classifier to be used

        Returns:
            prediction: Class of high
                Higher high = 1
                Lower high = -1

        """
        # Process highs
        prediction = self._prediction.high(
            self.feature_vector, bayesian=bayesian)

        # Return
        return prediction

    def low(self, bayesian=True):
        """Provide prediction of a low.

        Args:
            bayesian:
                True if bayesian classifier to be used
                False if linear classifier to be used

        Returns:
            prediction: Class of low
                Higher low = 1
                Lower low = -1

        """
        # Process lows
        prediction = self._prediction.low(
            self.feature_vector, bayesian=bayesian)

        # Return
        return prediction


class BlackBox(object):
    """Class to predict all outcomes.

    Args:
        None

    Returns:
        None

    Methods:

    """

    def __init__(self, extract, components=10):
        """Method for intializing the class.

        Args:
            extract: feature.Extract object
            components: Number principal components to use

        Returns:
            None

        """
        # Initialize key variables
        self.components = components

        # Do prediction
        timestamps = extract.timestamps()
        fxdata = extract.fxdata()
        last_timestamp = timestamps[-1]

        # Create feature vector
        self.feature_vector = feature.vector(fxdata, last_timestamp)

        # Get feature vectors for entire sample set
        self.feature_vectors = extract.vectors()

        # Get list of classes for feature vectors
        self.klasses_high = extract.classes_high(kessler=True)
        self.klasses_low = extract.classes_low(kessler=True)

    def high(self, feature_vector, bayesian=True):
        """Provide prediction of a high.

        Args:
            feature_vector: Feature vector on which to base prediction
            bayesian:
                True if bayesian classifier to be used
                False if linear classifier to be used

        Returns:
            prediction: Class of high
                Higher high = 1
                Lower high = -1

        """
        # Process highs
        if bayesian is True:
            # Bayesian classifier methodology
            pca_highs = pca.PCA(self.feature_vectors, self.klasses_high)
            bayes_classifier = classifier.Bayesian(
                pca_highs, components=self.components)
            prediction = bayes_classifier.classifier(feature_vector)
        else:
            # Linear classifier methodology
            linear_classifier = classifier.Linear(feature_vectors)
            prediction = linear_classifier.classifier(
                feature_vector, self.klasses_high)

        # Return
        return prediction

    def low(self, feature_vector, bayesian=True):
        """Provide prediction of a low.

        Args:
            feature_vector: Feature vector on which to base prediction
            bayesian:
                True if bayesian classifier to be used
                False if linear classifier to be used

        Returns:
            prediction: Class of low
                Higher low = 1
                Lower low = -1

        """
        # Process lows
        if bayesian is True:
            # Bayesian classifier methodology
            pca_lows = pca.PCA(self.feature_vectors, self.klasses_low)
            bayes_classifier = classifier.Bayesian(
                pca_lows, components=self.components)
            prediction = bayes_classifier.classifier(feature_vector)
        else:
            # Linear classifier methodology
            linear_classifier = classifier.Linear(feature_vectors)
            prediction = linear_classifier.classifier(
                feature_vector, self.klasses_low)

        # Return
        return prediction
