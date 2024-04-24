import numpy as np
class QTable:
    def __init__(self):
        """
        Constructor
        """
        try:
            self.table = np.load("Q_learning_model.npy", allow_pickle=True).item()  # Load the pre-trained Q-table from q_table.npy
        except FileNotFoundError:
            self.table = {}  # Create a new empty Q-table if the file is not found

    def predict(self, feature):
        """
        Predict the command based on the given feature using the Q-table
        """
        # Convert the feature to a tuple for dictionary lookup
        feature_tuple = tuple(feature)
        nearest_feature = self.find_nearest_feature(feature_tuple)
        # Check if the feature is already in the Q-table
        if feature_tuple in self.table:
            # Return the command with the highest Q-value for the given feature
            return max(self.table[feature_tuple], key=self.table[feature_tuple].get)
        # If the feature is not in the Q-table, find the nearest feature
        elif nearest_feature is not None:
            # Return the command with the highest Q-value for the nearest feature
            # print("Use the nearest feature in Q-table")
            return max(self.table[nearest_feature], key=self.table[nearest_feature].get)
        else:
            # If no nearest feature is found, return a random command
            # print("Feature not found in Q-table")
            return np.random.choice(["MOVE_LEFT", "MOVE_RIGHT"])

    def update(self, feature, command, reward):
        """
        Update the Q-table based on the given feature, command, reward, and next feature
        """
        # Convert the feature and next feature to tuples for dictionary lookup
        feature_tuple = tuple(feature)
        
        # Check if the feature is already in the Q-table
        if feature_tuple not in self.table:
            # Initialize the Q-values for the feature with zeros
            self.table[feature_tuple] = {"MOVE_LEFT": 0, "MOVE_RIGHT": 0, "NONE" : 0}
        
        # Calculate the maximum Q-value for the next feature
        max_q_value = max(self.table[feature_tuple].values())
        
        # Update the Q-value for the current feature and command using the Q-learning formula
        self.table[feature_tuple][command] += 0.1 * (reward + 0.9 * max_q_value - self.table[feature_tuple][command])
    def augment(self, feature, command, reward,number):

        for _ in range(number):
            feature += np.random.randint(-5, 6)
            feature_tuple = tuple(feature)
            self.update(feature_tuple, command, reward)
        

    def save_table(self, file_path):
        """
        Save the Q-table to a file
        """
        np.save(file_path, self.table)
    def find_nearest_feature(self, feature):
        """
        Find the nearest feature in the Q-table based on the given feature
        """
        nearest_feature = None
        min_distance = float('inf')
        
        # Iterate over all features in the Q-table
        for q_feature in self.table.keys():
            # Calculate the Euclidean distance between the given feature and the Q-table feature
            distance = np.linalg.norm(np.array(feature) - np.array(q_feature))
            
            # Update the nearest feature if the distance is smaller than the current minimum distance
            if distance < min_distance:
                min_distance = distance
                nearest_feature = q_feature
        
        return nearest_feature
