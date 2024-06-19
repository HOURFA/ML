import pickle
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_graphviz
import subprocess
def combined_dataset(data_path, model_name):
    # Load the data for 1P and 2P
    with open(f'{data_path}/targets_{model_name}_1P.pickle', 'rb') as f:
        targets_1P = pickle.load(f)
        
    with open(f'{data_path}/features_{model_name}_1P.pickle', 'rb') as f:
        features_1P = pickle.load(f)

    with open(f'{data_path}/targets_{model_name}_2P.pickle', 'rb') as f:
        targets_2P = pickle.load(f)
    with open(f'{data_path}/features_{model_name}_2P.pickle', 'rb') as f:
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
    with open(f'{data_path}/targets_{model_name}_2P.pickle', 'wb') as f:
        pickle.dump(unique_targets_list, f)
    with open(f'{data_path}/features_{model_name}_2P.pickle', 'wb') as f:
        pickle.dump(unique_features_list, f)
    with open(f'{data_path}/targets_{model_name}_1P.pickle', 'wb') as f:
        pickle.dump(unique_targets_list, f)
    with open(f'{data_path}/features_{model_name}_1P.pickle', 'wb') as f:
        pickle.dump(unique_features_list, f)    


# def visualize_tree(model, features, targets, model_name):
#     # Define the model
#     model = DecisionTreeClassifier(
#         max_depth=None,
#         min_samples_split=2,
#         min_samples_leaf=1,
#         criterion="entropy",
#         max_features=None
#     )

#     # Fit the model with the deduplicated data
#     model.fit(features, targets)

#     # Export the model to a .dot file
if __name__ == "__main__":
    model_name = "TANK"
    model_path = r"C:\Users\abc78\ML\TankMan-main\SourceCode\ml\model_TANK_1P.pickle"
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    if model_name == "STRATEGY":
        feature_name = ['oil', 'bullet']
        class_name = ['FIND_OIL', 'FIND_BULLET', 'FIND_ENEMY']
    elif model_name == "TANK":
        feature_name = ['x', 'y', 'otherside_x', 'otherside_y', 'angle', 'direction', 'distance', 'iswallorenemy']
        class_name = ['TURN_RIGHT', 'TURN_LEFT', 'FORWARD', 'BACKWARD',  'DONTMOVE']
    elif model_name == "GUN":
        feature_name = ['angle', 'direction']
        class_name = ['SHOOT', 'AIM_RIGHT', 'AIM_LEFT']

    export_graphviz(
        model, 
        out_file='model.dot',
        filled=True, 
        rounded=True,
        special_characters=True,
        feature_names=feature_name,
        class_names=class_name
    )

    # Convert the .dot file to a .png file
    subprocess.run("dot -Tpng model.dot -o model.png", shell=True)
