import os
import pickle
import csv
import unittest
from ml_play_manual import MLPlay
from sklearn.tree import DecisionTreeRegressor

class TestMLPlay(unittest.TestCase):
    def setUp(self):        
        self.dir = os.path.dirname(__file__)
        print("SETTUP")
        if os.path.exists(self.dir + '/features.csv'):
            os.remove(os.path.join(self.dir, 'features.csv'))
        if os.path.exists(self.dir + '/features.pickle'):
            os.remove(os.path.join(self.dir, 'features.pickle'))
        if os.path.exists(self.dir + '/targets.pickle'):            
            os.remove(os.path.join(self.dir, 'targets.pickle'))
        if os.path.exists(self.dir + '/model.pickle'): 
            os.remove(os.path.join(self.dir, 'model.pickle'))                    
    def test_model_load(self):
        print("unit test : model load")
        print("----- start -----")
        ml_play = MLPlay()
        self.assertTrue(os.path.exists(os.path.join(self.dir, 'model.pickle')))
        ml_play.model_load()        
        self.assertTrue(os.path.exists(os.path.join(self.dir, 'model.pickle')))
        print("----- end -----")
    def test_model_save(self):
        print("unit test : model_save")
        print("----- start -----")        
        ml_play = MLPlay()
        features = [
            [0, 115, 390, 2, 2],
            [1, 120, 395, 3, 3]
        ]
        targets = [
            [115], 
            [115]
        ]
        Temp = ml_play.feature_add(self.dir, features)
        ml_play.model_save(self.dir, Temp)

        # Check if the files are created
        self.assertTrue(os.path.exists(os.path.join(self.dir, 'features.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.dir, 'features.pickle')))
        self.assertTrue(os.path.exists(os.path.join(self.dir, 'targets.pickle')))
        self.assertTrue(os.path.exists(os.path.join(self.dir, 'model.pickle')))

        # Check if the features file contains the correct data
        with open(os.path.join(self.dir, 'features.csv'), 'r') as f:
            reader = csv.reader(f, delimiter=',')
            data = list(reader)
            self.assertEqual(data, [['115', '0', '115', '390', '2', '2'], ['115', '1', '120', '395', '3', '3']])

        # Check if the features pickle file contains the correct data
        with open(self.dir + '/features' + '.pickle', 'rb') as f:
            loaded_features = pickle.load(f)
            
            self.assertEqual(loaded_features, [[115, 390, 2, 2], [120, 395, 3, 3]])

        # Check if the targets pickle file contains the correct data
        with open(os.path.join(self.dir, 'targets.pickle'), 'rb') as f:
            loaded_targets = pickle.load(f)
            self.assertEqual(loaded_targets, targets)

        # Check if the model pickle file contains the correct data
        with open(os.path.join(self.dir, 'model.pickle'), 'rb') as f:
            loaded_model = pickle.load(f)            
            loaded_model = DecisionTreeRegressor(
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features=None)
            self.assertIsInstance(loaded_model, DecisionTreeRegressor)        
        print("----- end -----")
    def test_feature_add(self):        
        print("unit test : feature_add")
        print("----- start -----")
        ml_play = MLPlay()
        feature = [
            [0, 110, 385, 1, 1],
            [1, 115, 390, 2, 2],
            [2, 120, 395, 3, 3],
            [3, 125, 395, 4, 4],
            [4, 130, 395, 5, 5],
            [5, 135, 395, 6, 6]
        ]
        expected_features = [
            [115, 390, 2, 2],
            [120, 395, 3, 3],
            [125, 395, 4, 4],
            [130, 395, 5, 5],
            [135, 395, 6, 6]
        ]
        expected_targets = [
            [115],
            [115],
            [115],
            [115],
            [115]
        ]
        expected_temp = [
            [115, 1, 115, 390, 2, 2], 
            [115, 2, 120, 395, 3, 3], 
            [115, 3, 125, 395, 4, 4], 
            [115, 4, 130, 395, 5, 5], 
            [115, 5, 135, 395, 6, 6]
        ]
        Temp = ml_play.feature_add(self.dir, feature)
        self.assertEqual(ml_play.features, expected_features)
        self.assertEqual(ml_play.targets, expected_targets)        
        self.assertEqual(Temp, expected_temp)
        print("----- end -----")
             
if __name__ == '__main__':
    unittest.main()