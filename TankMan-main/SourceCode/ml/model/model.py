import os
import pickle
from sklearn.tree import DecisionTreeClassifier
from ml.model.constant import defaultdict

class DecisionTreeClassifier_Model:
    """
    A class representing a Decision Tree Classifier model.

    Attributes:
        model_name (str): The name of the model.
        dir_path (str): The directory path where the model and data files are stored.
        model (DecisionTreeClassifier): The decision tree classifier model.
        features (list): The features used for training the model.
        targets (list): The target values used for training the model.

    Methods:
        load_data(): Loads the features and targets from pickle files or initializes them from a dictionary.
        load_model(max_depth): Loads the model from a pickle file or creates a new model if the file doesn't exist.
        save_model(): Saves the features, targets, and model to pickle files.
        predict(feature): Predicts the target value for a given feature.
        train(): Trains the model using the features and targets.

    """

    def __init__(self, model_name, dir_path, max_depth=None):
        self.model_name = model_name
        self.dir_path = dir_path
        self.model = self.load_model(max_depth)
        self.features = []
        self.targets = []

    def load_data(self):
        """
        Loads the features and targets from pickle files or initializes them from a dictionary.
        If the pickle files don't exist, the features and targets are initialized from a dictionary.

        """
        try:
            with open(os.path.join(self.dir_path, f"features_{self.model_name}.pickle"), 'rb') as f:
                self.features = pickle.load(f)
            with open(os.path.join(self.dir_path, f"targets_{self.model_name}.pickle"), 'rb') as f:
                self.targets = pickle.load(f)
        except Exception:
            self.features = defaultdict[self.model_name]["feature"]
            self.targets = defaultdict[self.model_name]["target"]

    def load_model(self, max_depth=None):
        """
        Loads the model from a pickle file or creates a new model if the file doesn't exist.
        If the model file doesn't exist, a new DecisionTreeClassifier model is created and trained using the features and targets.

        Args:
            max_depth (int, optional): The maximum depth of the decision tree. Defaults to None.

        Returns:
            DecisionTreeClassifier: The loaded or created decision tree classifier model.

        """
        model = None
        model_path = os.path.join(self.dir_path, f"model_{self.model_name}.pickle")
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        except Exception:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            model = DecisionTreeClassifier(max_depth=max_depth,
                                           min_samples_split=2,
                                           min_samples_leaf=1,
                                           max_features=None)
            self.load_data()
            model.fit(self.features, self.targets)
        return model

    def save_model(self):
        """
        Saves the features, targets, and model to pickle files.

        """
        with open(os.path.join(self.dir_path, f"features_{self.model_name}.pickle"), 'wb') as f:
            pickle.dump(self.features, f)
        with open(os.path.join(self.dir_path, f"targets_{self.model_name}.pickle"), 'wb') as f:
            pickle.dump(self.targets, f)
        with open(os.path.join(self.dir_path, f"model_{self.model_name}.pickle"), 'wb') as f:
            pickle.dump(self.model, f)

    def predict(self, feature):
        """
        Predicts the target value for a given feature.

        Args:
            feature (list): The feature values for prediction.

        Returns:
            The predicted target value.

        """
        return self.model.predict([feature])[0]

    def train(self):
        """
        Trains the model using the features and targets.

        """
        self.model.fit(self.features, self.targets)

