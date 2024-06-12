import os
import pickle
from sklearn.tree import DecisionTreeClassifier
from ml.model.constant import defaultdict

class DecisionTreeClassifier_Model:
    def __init__(self, model_name, dir_path, max_depth = None):
        self.model_name = model_name
        self.dir_path = dir_path
        self.model = self.load_model(max_depth)
        self.features, self.targets = self.load_data()

    def load_data(self):
        features, targets = [], []
        try:
            with open(os.path.join(self.dir_path, f"features_{self.model_name}.pickle"), 'rb') as f:
                features = pickle.load(f)
            with open(os.path.join(self.dir_path, f"targets_{self.model_name}.pickle"), 'rb') as f:
                targets = pickle.load(f)
        except Exception:
            features = defaultdict[self.model_name]["feature"]
            targets = defaultdict[self.model_name]["target"]
        return features, targets
    def load_model(self , max_depth=None):
        model = None
        model_path = os.path.join(self.dir_path, f"model_{self.model_name}.pickle")
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)        
        else:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            model = DecisionTreeClassifier(max_depth=max_depth,
                                            min_samples_split=2,
                                            min_samples_leaf=1,
                                            max_features=None) 
                      
            features, targets = self.load_data()
            model.fit(features, targets)
        return model
    def save_model(self):
        with open(os.path.join(self.dir_path, f"features_{self.model_name}.pickle"), 'wb') as f:
            pickle.dump(self.features, f)
        with open(os.path.join(self.dir_path, f"targets_{self.model_name}.pickle"), 'wb') as f:
            pickle.dump(self.targets, f)
        with open(os.path.join(self.dir_path, f"model_{self.model_name}.pickle"), 'wb') as f:
            pickle.dump(self.model, f) 

    def predict(self,feature):

        return self.model.predict([feature])[0]

    def train(self):

        self.model.fit(self.features, self.targets)

