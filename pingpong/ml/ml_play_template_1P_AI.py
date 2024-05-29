"""
The template of the script for the machine learning process in game pingpong
"""
import pygame
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
import os
import pickle
import csv
import random
import time
import datetime
# python -m mlgame -i ./ml/ml_play_template_1P.py -i ./ml/ml_play_template_2P.py  ./ --difficulty HARD --game_over_score 3  --init_vel 10
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
        self.model_load()
        self.features = []
        self.ball_served = False
        self.record = []
        self.targets = []        
        if self.side == "1P":
            self.HIT_POINT_Y = 420
            self.NEGATIVE_HIT_POINT_Y = False
            self.OTHERSIDE = "2P"
        elif self.side == "2P":
            self.HIT_POINT_Y = 80
            self.NEGATIVE_HIT_POINT_Y = True
            self.OTHERSIDE = "1P"
        self.offset = 20
        self.ball_speed = 0
        self.WIDTH = 200
        self.HEIGHT = 500

    def update(self, scene_info, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] == f"GAME_{self.OTHERSIDE}_WIN":
            self.learn = True
            return "RESET"
        command = "NONE"
        self.ball_speed = abs(scene_info["ball_speed"][0])
        if scene_info["serving_side"] == self.side and self.ball_served == False :
            command = random.choice(["SERVE_TO_LEFT", "SERVE_TO_RIGHT"])
            # command = "SERVE_TO_RIGHT"
            self.ball_served = True
        elif self.ball_speed > 0:
            platformX = scene_info[f"platform_{self.side}"][0]
            x, y = scene_info['ball']
            feature = self.feature_get(scene_info)            
            if self.model is not None and ( y > (self.HIT_POINT_Y - self.ball_speed) if self.NEGATIVE_HIT_POINT_Y else y < (self.HIT_POINT_Y + self.ball_speed) ):
                
                if random.random() > 0.05:#一定機率不套用模型                     
                    targetX = self.predict(feature)                    
                    targetX = self.postprocess(targetX)
                    if (platformX + self.offset) > targetX:
                        command = "MOVE_LEFT"
                    elif (platformX + self.offset) < targetX:
                        command = "MOVE_RIGHT"
                    else:
                        command = "NONE"
                else:
                    command = random.choice(["MOVE_LEFT", "MOVE_RIGHT"])
            
            # if y > self.HIT_POINT_Y:
            #     print(f"platformX: {platformX + self.offset}, targetX: {targetX}, ball_x: {x}, ball_y: {y}")
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

            self.model = DecisionTreeRegressor(
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features=None)

            self.train(self.features, self.targets)

            self.model_save(DIR, Temp)
        self.learn = False
        self.ball_served = False

    def feature_get(self, scene_info):

        frame = scene_info['frame']
        x, y = scene_info['ball']     
        dx, dy = 0, 0

        if frame > 0 and len(self.record) > 0:
            lastFrame, lastX, lastY, last_dx, last_dy = self.record[-1][0:5]
            dx, dy = last_dx, last_dy

            if frame - lastFrame == 1:
                dx, dy = (x - lastX), (y - lastY)
        
        fv = [frame, x / self.WIDTH, y / self.HEIGHT, dx / self.WIDTH, dy /  self.HEIGHT]
        
        self.record.append(fv)

        return fv
    
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
            print("-----Creat a New Model-----")
        with open(DIR + f"/model_{self.side}.pickle", 'rb') as f:
            self.model = pickle.load(f)
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

        with open(DIR + f"/features_{self.side}" + '.pickle', 'wb') as f:
            pickle.dump(self.features, f)
        with open(DIR + f"/targets_{self.side}" + '.pickle', 'wb') as f:
            pickle.dump(self.targets, f)

        with open(DIR+ f"/model_{self.side}" + '.pickle', 'wb') as f:
            pickle.dump(self.model, f)

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
        
        if os.path.exists(DIR + f"/targets_{self.side}.pickle"):
            with open(DIR + f"/targets_{self.side}.pickle", 'rb') as f:
                self.targets = pickle.load(f)
            with open(DIR + f"/features_{self.side}.pickle", 'rb') as f:
                self.features = pickle.load(f)
        ii = None
        for i in range(len(feature)):
            y = feature[i][2] * self.HEIGHT
            if y <= (self.HIT_POINT_Y + self.ball_speed) and y >= (self.HIT_POINT_Y - self.ball_speed):
                ii = i
                break        
        targetX = int(feature[ii][1] * self.WIDTH)
        Temp = []
        i = 0
        for fv in feature[ii:]:
            frame, x, y, dx, dy = fv[0:5]
            y *= self.HEIGHT
            self.features.append(fv[1:])
            self.targets.append([targetX])
            temp = [targetX]
            temp.extend(fv[1:])
            Temp.append(temp)
            i += 1
            if i > self.ball_speed * 5 and (y <= self.HIT_POINT_Y if self.NEGATIVE_HIT_POINT_Y else y >= self.HIT_POINT_Y):
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
        targetX = int(self.model.predict([feature[1:]])[0])
        return targetX
    
    def postprocess(self, number):
        rounded_number = round(number)
        remainder = rounded_number % 5
        if remainder <= 2.5:
            return rounded_number - remainder
        else:
            return rounded_number + (5 - remainder)    


