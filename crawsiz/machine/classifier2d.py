#!/usr/bin/env python3
"""Program creates histograms."""

# Standard python imports
import math

# Non-standard python imports
import numpy as np

# Our library imports
from machine import pca


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
        self.data = _get_data(pca_object, components=self.components)
        self.class_list = self.pca_object.classes()

        # Get new PCA object for principal components
        self.pca_new = pca.PCA(self.data)

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
                accuracy[cls] = 100 * (correct[cls] / cls_count[cls])

            # Keep a tally for all successes
            correct[None] = correct[None] + correct[cls]
            cls_count[None] = cls_count[None] + cls_count[cls]

        # Calulate overall accuracy
        accuracy[None] = 100 * (correct[None] / cls_count[None])

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


def _get_data(pca_object, components=2):
    """Method for intializing the class.

    Args:
        classes: List of classes to process
        pca_object: PCA class object

    Returns:
        None

    """
    # Initialize key variables
    data = []

    # Convert pca_object data to data acceptable by the Histogram2D class
    (principal_classes,
     principal_components) = pca_object.principal_components(
         components=components)

    for idx, cls in enumerate(principal_classes):
        dimensions = principal_components[idx, :]
        data.append(
            (cls, dimensions.tolist())
        )

    # Return
    return data
