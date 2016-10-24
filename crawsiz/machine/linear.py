"""Class for principal component analysis."""

# Standard python imports

# Non-standard python imports
import numpy as np


class Linear(object):
    """Class for principal component analysis.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        get_cli:
    """

    def __init__(self, feature_vectors):
        """Function for intializing the class.

        Args:
            feature_vectors: Numpy array of feature vectors

        """
        # Initialize key variables
        (rows, _) = feature_vectors.shape

        # Append a column of ones to array
        ones = np.ones((rows, 1))
        kessler_array = np.hstack((ones, feature_vectors))

        # Make array available to rest of class
        self.data = kessler_array.tolist()

    def classifier(self, classes):
        """Create binary linear classifier.

        Args:
            classes: List of class definitions for training data

        Returns:
            result: Classifier

        """
        # Initialize key variables
        pseudo = np.linalg.pinv(self.data)
        result = np.dot(pseudo, classes)
        return result

    def prediction(self, feature_vector, classes):
        """Predict the class of the vector.

        Args:
            feature_vector: Feature vector

        Returns:
            result: Class of prediction

        """
        # Prepend a "1" to the vector
        ones = np.ones((1, ))
        vector = np.hstack((ones, feature_vector))

        # Classify
        classification = np.dot(vector, self.classifier(classes))

        # Return
        result = kessler_to_number(classification)
        return result


def kessler_to_number(classification):
    """Predict the class of the vector.

    Args:
        vector: Vector

    Returns:
        result: Class of prediction

    """
    # Initialize key variables
    (columns,) = classification.shape

    # Make the prediction
    if columns == 1:
        # Binary classifier
        if classification[0] > 0:
            result = 1
        else:
            result = -1
    else:
        # Non-binary classifier
        values = classification.tolist()
        maximum = max(values)
        result = values.index(maximum)

    return result
