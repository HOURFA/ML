import pickle
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
import subprocess
import time
target = "TANK"
path_extend = ""
start = time.time()
# Load the data for 1P and 2P
with open(f'ml/{path_extend}/targets_{target}_1P.pickle', 'rb') as f:
    targets_1P = pickle.load(f)
    
with open(f'ml/{path_extend}/features_{target}_1P.pickle', 'rb') as f:
    features_1P = pickle.load(f)

with open(f'ml/{path_extend}/targets_{target}_2P.pickle', 'rb') as f:
    targets_2P = pickle.load(f)
with open(f'ml/{path_extend}/features_{target}_2P.pickle', 'rb') as f:
    features_2P = pickle.load(f)
# Combine the datasets
combined_targets = np.concatenate((targets_1P, targets_2P))
combined_features = np.concatenate((features_1P, features_2P))

# Combine features and targets for deduplication
combined_data = np.hstack((combined_features, combined_targets.reshape(-1, 1)))

# Remove duplicate rows
unique_data = np.unique(combined_data, axis=0)

# Split the unique data back into features and targets
unique_features = unique_data[:, :-1]
unique_targets = unique_data[:, -1]

# Convert np.ndarray to list
unique_features_list = unique_features.tolist()
unique_targets_list = unique_targets.tolist()

# Save the deduplicated combined dataset
with open(f'ml/{path_extend}/targets_{target}_2P.pickle', 'wb') as f:
    pickle.dump(unique_targets_list, f)
with open(f'ml/{path_extend}/features_{target}_2P.pickle', 'wb') as f:
    pickle.dump(unique_features_list, f)
with open(f'ml/{path_extend}/targets_{target}_1P.pickle', 'wb') as f:
    pickle.dump(unique_targets_list, f)
with open(f'ml/{path_extend}/features_{target}_1P.pickle', 'wb') as f:
    pickle.dump(unique_features_list, f)    

# Define the model
model = DecisionTreeClassifier(
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    criterion="entropy",
    max_features=None
)

# Fit the model with the deduplicated data
model.fit(unique_features_list, unique_targets_list)

# Export the model to a .dot file
if target == "STRATEGY":
    feature_name = ['oil', 'bullet']
    class_name = ['FIND_OIL', 'FIND_BULLET', 'FIND_ENEMY']
elif target == "TANK":
    feature_name = ['x', 'y', 'otherside_x', 'otherside_y', 'angle', 'direction', 'distance', 'iswallorenemy']
    class_name = ['TURN_RIGHT', 'TURN_LEFT', 'FORWARD', 'BACKWARD',  'DONTMOVE']
elif target == "GUN":
    feature_name = ['angle', 'direction']
    class_name = ['SHOOT', 'AIM_RIGHT', 'AIM_LEFT']

export_graphviz(
    model, 
    out_file='ml/model.dot',
    filled=True, 
    rounded=True,
    special_characters=True,
    feature_names=feature_name,
    class_names=class_name
)

# Convert the .dot file to a .png file
# subprocess.run("dot -Tpng ml/model.dot -o ml/model.png", shell=True)
