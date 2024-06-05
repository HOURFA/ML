from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
import os
import pickle
import csv
import random

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param ai_name A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.side = ai_name
        self.model = None
        self.learn = False
        self.ball_served = False
        self.ball_catch_time = 0
        self.model_load()
        self.features = []        
        self.record = []
        self.targets = []        
        if self.side == "1P":
            self.OTHERSIDE = "2P"
            self.HIT_POINT_Y = 415
            self.NEGATIVE_HIT_POINT_Y = False            
        elif self.side == "2P":
            self.OTHERSIDE = "1P"
            self.HIT_POINT_Y = 80
            self.NEGATIVE_HIT_POINT_Y = True            
        self.offset_to_platform_center = 20
        self.ball_speed_x, self.ball_speed_y = 0, 0
        self.WIDTH = 200
        self.HEIGHT = 500
        self.DRAW_BALL_SPEED = 40
        self.plateform_speed = 5

    def update(self, scene_info, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] == f"GAME_{self.OTHERSIDE}_WIN":
            self.learn = True
            with open(f'ball_catch_times_{self.side}' + '.csv', 'a', newline='') as f:
                data = [self.ball_catch_time]
                csv.writer(f).writerow(data)
            self.ball_catch_time = 0
            return "RESET"
        command = "NONE"
        self.ball_speed_x,self.ball_speed_y  = scene_info["ball_speed"][0], scene_info["ball_speed"][1]
        if scene_info["serving_side"] == self.side and self.ball_served == False :
            command = random.choice(["SERVE_TO_LEFT", "SERVE_TO_RIGHT"])
            self.ball_served = True
        elif abs(self.ball_speed_y) > 0:
            platformX = scene_info[f"platform_{self.side}"][0]
            y = scene_info['ball'][1]
            feature = self.preprocess(scene_info)                        
            if self.model is not None and ( y > (self.HIT_POINT_Y) if self.NEGATIVE_HIT_POINT_Y else y < (self.HIT_POINT_Y) ):                
                if random.random() > 0.05 :                 
                    targetX = self.predict(feature)                                           
                    targetX = self.postprocess(targetX)
                    if (platformX + self.offset_to_platform_center) > targetX:
                        command = "MOVE_LEFT"
                    elif (platformX + self.offset_to_platform_center) < targetX:
                        command = "MOVE_RIGHT"
                    else:
                        if y - abs(self.ball_speed_y) * 2 <= self.HIT_POINT_Y if self.NEGATIVE_HIT_POINT_Y else  y + abs(self.ball_speed_y) * 2 >= self.HIT_POINT_Y:
                            command = "MOVE_RIGHT" if feature[3] > 0 else "MOVE_LEFT"
                        else:
                            command = "NONE"
                else:
                    command = random.choice(["MOVE_LEFT", "MOVE_RIGHT", "NONE"])
            if y == self.HIT_POINT_Y and self.ball_speed_x != 0:
                self.ball_catch_time += 1
        return command

    def reset(self):
        """
        Reset the status
        """        
        if self.learn:
            print(f"================{self.side}_LEARN================")
            DIR = os.path.dirname(__file__)
            with open(DIR + f"/record_{self.side}" + '.csv', 'w', newline='') as f:
                csv.writer(f, delimiter=',').writerows(self.record)
            self.record.reverse()

            Temp = self.feature_add(DIR, self.record)

            self.model = DecisionTreeRegressor( max_depth=None,
                                                min_samples_split=2,
                                                min_samples_leaf=1,
                                                max_features=None )

            self.train(self.features, self.targets)
            self.model_save(DIR, Temp)
            self.learn = False

        self.ball_served = False

    def preprocess(self, scene_info):
        """
        Preprocesses the scene information and returns a feature vector.

        Args:
            scene_info (dict): A dictionary containing the scene information.

        Returns:
            list: A feature vector containing the preprocessed information.

        """
        frame = scene_info['frame']
        x, y = scene_info['ball']     

        feature = [frame, 
                   x / self.WIDTH, 
                   y / self.HEIGHT, 
                   self.ball_speed_x / self.DRAW_BALL_SPEED, 
                   self.ball_speed_y / self.DRAW_BALL_SPEED
                   ]
        
        self.record.append(feature)

        return feature
    
    def model_load(self):
        """
        Loads a pre-trained model from a pickle file.

        The method checks if the 'model.pickle' file exists in the same directory as the script.
        If the file exists, it loads the model from the pickle file and assigns it to the 'model' attribute of the class.
        If the file does not exist, creat a new model.

        Returns:
            None
        """
        DIR = os.path.dirname(__file__)
        if not os.path.exists(DIR + f"/model_{self.side}.pickle"):
            with open(DIR+f"/model_{self.side}.pickle", 'wb') as f:
                pickle.dump(None, f)
                f.flush()
                os.fsync(f.fileno())
            print("-----Creat a New Model-----")
        with open(DIR + f"/model_{self.side}.pickle", 'rb') as f:
            try:
                self.model = pickle.load(f)
            except EOFError:
                pass
        print("-----Model Loaded-----")

    def model_save(self, DIR, features):
        """
        Save the model, features, and targets to the specified directory.

        Args:
            DIR (str): The directory path where the files will be saved.
            features (list): The list of features to be saved.

        Returns:
            None
        """
        with open(DIR + f"/features_{self.side}" + '.csv', 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(features)
        if self.features is not None:
            with open(DIR + f"/features_{self.side}" + '.pickle', 'wb') as f:
                pickle.dump(self.features, f)
                f.flush()
                os.fsync(f.fileno())
        if self.targets is not None:
            with open(DIR + f"/targets_{self.side}" + '.pickle', 'wb') as f:
                pickle.dump(self.targets, f)
                f.flush()
                os.fsync(f.fileno())
        if self.model is not None:
            with open(DIR+ f"/model_{self.side}" + '.pickle', 'wb') as f:
                pickle.dump(self.model, f)
                f.flush()
                os.fsync(f.fileno())

    def feature_add(self, DIR, feature):
        """
        Adds features to the existing feature set and updates the target values.

        Args:
            DIR (str): The directory path where the feature and target files are stored.
            feature (list): A list of feature.

        Returns:
            list: A list of feature records with the target values updated.

        Raises:
            FileNotFoundError: If the feature or target files are not found in the specified directory.
        """
        if os.path.exists(DIR + f"/targets_{self.side}.pickle") :
            with open(DIR + f"/targets_{self.side}.pickle", 'rb') as f:
                try:
                    self.targets = pickle.load(f)     
                except EOFError:
                    print("-----No Target File-----")
        if os.path.exists(DIR + f"/features_{self.side}.pickle"):
            with open(DIR + f"/features_{self.side}.pickle", 'rb') as f:
                try:
                    self.features = pickle.load(f)
                except EOFError:
                    print("-----No Features File-----")
        ii = None
        for i in range(len(feature)):
            y = feature[i][2] * self.HEIGHT
            if y <= (self.HIT_POINT_Y + abs(self.ball_speed_y)) and y >= (self.HIT_POINT_Y - abs(self.ball_speed_y)):
                ii = i
                break        
        targetX = int(feature[ii][1] * self.WIDTH)
        Temp = []
        i = 0
        for fv in feature[ii:]:
            y = fv[2] * self.HEIGHT
            self.features.append(fv[1:])
            self.targets.append([targetX])
            temp = [targetX]
            temp.extend(fv[1:])
            Temp.append(temp)
            i += 1
            if i > abs(self.ball_speed_y) and (y <= self.HIT_POINT_Y if self.NEGATIVE_HIT_POINT_Y else y >= self.HIT_POINT_Y):
                break 
        return Temp

    def train(self, features, targets):
        """
        Trains the model using the provided features and targets.

        Parameters:
        - features (list): The input features for training the model.
        - targets (list): The target values for training the model.

        Returns:
        None
        """        
        self.model.fit(features, targets)

    def predict(self, feature):
        """
        Predicts the target X coordinate based on the given feature.

        Parameters:
        - feature (list): A list of features used for prediction.

        Returns:
        - targetX (int): The predicted target X coordinate.

        """        
        targetX = self.model.predict([feature[1:]])[0]
        return targetX
    
    def postprocess(self, number):
        """
        Rounds the given number and performs additional processing.

        Args:
            number (float): The number to be processed.

        Returns:
            int: The processed number.

        """
        rounded_number = round(number)
        remainder = rounded_number % self.plateform_speed
        if remainder <= (self.plateform_speed / 2):
            return int(rounded_number - remainder)
        else:
            return int(rounded_number + (5 - remainder))


