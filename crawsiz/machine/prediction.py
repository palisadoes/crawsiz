"""Library to process the ingest of data files."""

# Standard imports

# Non standard imports

# Import custom libraries
from crawsiz.machine import pca
from crawsiz.machine import classifier
from crawsiz.main import feature


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

        # Create feature vector
        self.feature_vector = extract.last_vector()

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

        # Get feature vectors for entire sample set
        feature_vectors = extract.vectors()

        # Linear classifier methodology
        self.linear_classifier = classifier.Linear(feature_vectors)

        # Get list of classes for feature vectors
        self.klasses_high = extract.classes_high(kessler=True)
        self.klasses_low = extract.classes_low(kessler=True)

        # Bayesian classifier methodology (lows)
        pca_lows = pca.PCA(feature_vectors, self.klasses_low)
        self.bayes_classifier_lows = classifier.Bayesian(
            pca_lows, components=self.components)

        # Bayesian classifier methodology (highs)
        pca_highs = pca.PCA(feature_vectors, self.klasses_high)
        self.bayes_classifier_highs = classifier.Bayesian(
            pca_highs, components=self.components)

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
            prediction = self.bayes_classifier_highs.classifier(
                feature_vector)
        else:
            # Linear classifier methodology
            prediction = self.linear_classifier.classifier(
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
            prediction = self.bayes_classifier_lows.classifier(feature_vector)
        else:
            # Linear classifier methodology
            prediction = self.linear_classifier.classifier(
                feature_vector, self.klasses_low)

        # Return
        return prediction
