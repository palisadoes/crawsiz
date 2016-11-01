#!/usr/bin/env python3
"""Program creates histograms."""

# Standard python imports
import math

# Non-standard python imports
import numpy as np

# Our library imports
from crawsiz.machine import pca


class Bayesian(object):
    """Class for principal component analysis probabilities.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        get_cli:
    """

    def __init__(self, pca_object, components=2):
        """Method for intializing the class.

        Args:
            classes: List of classes to process
            pca_object: PCA class object

        Returns:
            None

        """
        # Initialize key variables
        self.components = components
        self.pca_object = pca_object

        # Convert pca_object data to data acceptable by the Histogram2D class
        self.class_list = self.pca_object.classes()

        # Get new PCA object for principal components
        (principal_classes,
         principal_components) = pca_object.principal_components(
             components=components)
        self.pca_new = pca.PCA(principal_components, principal_classes)

    def classes(self):
        """Get the classes.

        Args:
            cls: Class of data

        Returns:
            value: classes

        """
        # Return
        value = self.class_list
        return value

    def meanvector(self, cls):
        """Get the meanvector.

        Args:
            cls: Class of data

        Returns:
            value: meanvector

        """
        # Return
        value = self.pca_new.meanvector(cls=cls)
        return value

    def covariance(self, cls):
        """Get the covariance.

        Args:
            cls: Class of data

        Returns:
            value: covariance

        """
        # Return
        value = self.pca_new.covariance(cls=cls)
        return value

    def accuracy(self):
        """Calulate the accuracy of the training data using gaussian models.

        Args:
            None

        Returns:
            accuracy: Prediction accuracy

        """
        # Initialize key variables
        correct = {}
        prediction = 0
        cls_count = {}
        accuracy = {}

        # Analyze all the data
        for cls in self.pca_object.classes():
            # Get list of x values to test
            vectors = self.pca_object.xvalues(cls)

            # Process each vector
            for vector in vectors:
                # Get the prediction
                prediction = self.classifier(vector)

                # Only count definitive predictions
                if prediction is not None:
                    # Count the number of correct predictions
                    if prediction == cls:
                        if cls in correct:
                            correct[cls] += 1
                        else:
                            correct[cls] = 1

                    # Increment the count
                    if cls in cls_count:
                        cls_count[cls] += 1
                    else:
                        cls_count[cls] = 1

        # Calculate per class accuracy
        correct[None] = 0
        cls_count[None] = 0
        for cls in cls_count.keys():
            if cls_count[cls] != 0:
                accuracy[cls] = correct[cls] / cls_count[cls]

            # Keep a tally for all successes
            correct[None] = correct[None] + correct[cls]
            cls_count[None] = cls_count[None] + cls_count[cls]

        # Calulate overall accuracy
        accuracy[None] = correct[None] / cls_count[None]

        # Return
        return accuracy

    def classifier(self, xvalue):
        """Bayesian classifer for any value of X.

        Args:
            xvalue: Specific feature vector of X

        Returns:
            selection: Class classifier chooses

        """
        # Initialize key variables
        probability = {}
        classes = self.classes()

        # Get probability of each class
        probability = self.probability(xvalue)

        # Reassign variables for readability
        prob_c0 = probability[classes[0]]
        prob_c1 = probability[classes[1]]

        # Evaluate probabilities
        if prob_c0 + prob_c1 == 0:
            selection = None
        else:
            if prob_c0 > prob_c1:
                selection = classes[0]
            elif prob_c0 < prob_c1:
                selection = classes[1]
            else:
                selection = None

        # Return
        return selection

    def probability(self, xvalue):
        """Bayesian probability for any value of X.

        Args:
            xvalue: Specific feature vector of X

        Returns:
            selection: Class classifier chooses

        """
        # Initialize key variables
        probability = {}
        bayesian = {}
        classes = self.classes()

        # Calculate the principal components of the individual xvalue
        p1p2 = self.pca_object.pc_of_x(xvalue, self.components)

        # Get probability of each class
        for cls in classes:
            # Initialize values for the loop
            sample_count = len(self.pca_object.xvalues(cls))

            # Get values for calculating gaussian parameters
            dimensions = len(p1p2)
            x_mu = p1p2 - self.meanvector(cls)
            covariance = self.covariance(cls)
            inverse_cov = np.linalg.inv(covariance)
            determinant_cov = np.linalg.det(covariance)

            # Work on the exponent part of the bayesian classifer
            power = -0.5 * np.dot(np.dot(x_mu, inverse_cov), x_mu.T)
            exponent = math.pow(math.e, power)

            # Determine the constant value
            pipart = math.pow(2 * math.pi, dimensions / 2)
            constant = pipart * math.sqrt(determinant_cov)

            # Determine final bayesian
            bayesian[cls] = (sample_count * exponent) / constant

        # Calculate bayesian probability
        denominator = bayesian[classes[0]] + bayesian[classes[1]]
        for cls in classes:
            probability[cls] = bayesian[cls] / denominator

        # Return
        return probability


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

    def _classifier(self, classes):
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

    def classifier(self, feature_vector, classes):
        """Classify the feature vector.

        Args:
            feature_vector: Feature vector
            classes: list of classes

        Returns:
            result: Class of prediction

        """
        # Prepend a "1" to the vector
        ones = np.ones((1, ))
        vector = np.hstack((ones, feature_vector))

        # Classify
        classification = np.dot(vector, self._classifier(classes))

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
