"""
The template of the main script of the machine learning process
"""
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
import os
import pickle
import csv
import random
import math
import graphviz
import numpy as np
TURN_RIGHT = 0
TURN_LEFT = 1
FORWARD = 2
BACKWARD = 3

SHOOT = 0
AIM_RIGHT = 1
AIM_LEFT = 2

FIND_OIL = 0
FIND_BULLET = 1
FIND_ENEMY = 2

ANGLE_0 = 0
ANGLE_45 = 1
ANGLE_90 = 2
ANGLE_135 = 3
ANGLE_180 = 4
ANGLE_225 = 5
ANGLE_270 = 6
ANGLE_315 = 7
RADIUS = 300

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.side = ai_name
        self.DIR = os.path.dirname(__file__)
        print(f"Initial Game {ai_name} ml script")
        self.STRATEGY_MODEL = self.model_load("STRATEGY", max_depth= 3)
        self.STRATEGY_FEATURES = []
        self.STRATEGY_RECORD = []
        self.STRATEGY_TARGETS = []
        self.TANK_MODEL = self.model_load("TANK", max_depth= None)
        self.TANK_FEATURES = []
        self.TANK_RECORD = []
        self.TANK_TARGETS = []            
        self.GUN_MODEL = self.model_load("GUN", max_depth= None)   
        self.GUN_FEATURES = []
        self.GUN_RECORD = []
        self.GUN_TARGETS = []
        self.object = FIND_ENEMY
        self.WIDTH = 1000
        self.HEIGHT = 600    
        self.DONT_MOVE = False
        self.TANK_FRAME_COUNT = 0
        self.GUN_FRAME_COUNT = 0
        self.GUN_FLAG = False
        self.Diagonal = False
    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"        
        command = []
        x1, y1 = scene_info['x'], scene_info['y']
        x2, y2 = scene_info['competitor_info'][0]['x'], scene_info['competitor_info'][0]['y']
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)        
        feature = self.preprocess("STRATEGY", self.STRATEGY_RECORD, scene_info)
        object = self.predict(self.STRATEGY_MODEL, feature)  
        self.DONT_MOVE = False if (distance >= RADIUS) or object == 0 or object == 1 else True
        if object == 0: self.object = "oil_stations_info"
        elif object == 1: self.object = "bullet_stations_info"
        elif object == 2: self.object = "competitor_info"
        if not self.DONT_MOVE:
            feature = self.preprocess("TANK", self.TANK_RECORD, scene_info)
            if self.TANK_MODEL is not None:  
                if random.random() > 0.05 :       
                    target = self.predict(self.TANK_MODEL, feature)                             
                    if   target == TURN_RIGHT : command.append("TURN_RIGHT")
                    elif target == TURN_LEFT : command.append("TURN_LEFT")
                    elif target == FORWARD : command.append("FORWARD")
                    elif target == BACKWARD : command.append("BACKWARD")
                else:
                    command.append(random.choice(["TURN_RIGHT", "TURN_LEFT", "FORWARD", "BACKWARD"]))
            else:
                command.append("NONE")
            self.TANK_FRAME_COUNT += 1
        else:
            self.GUN_FLAG = True
            feature = self.preprocess("GUN", self.GUN_RECORD, scene_info)
            if self.GUN_MODEL is not None:  
                if random.random() > 0.05 :       
                    target = self.predict(self.GUN_MODEL, feature)                             
                    if target == AIM_LEFT : command.append("AIM_LEFT")
                    elif target == AIM_RIGHT : command.append("AIM_RIGHT")
                    elif target == SHOOT : command.append("SHOOT")
                else:
                    command.append((random.choice(["AIM_LEFT", "AIM_RIGHT", "SHOOT"])))
            else:
                command.append("NONE")            
            self.GUN_FRAME_COUNT += 1        
        return command

    def reset(self):
        """
        Reset the status
        """
        print(f"reset Game {self.side}")
        with open(self.DIR + f"/record_STRATEGY" + '.csv', 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(self.STRATEGY_RECORD)
        self.STRATEGY_RECORD.reverse()
        self.STRATEGY_FEATURES, self.STRATEGY_TARGETS = self.feature_add("STRATEGY", self.STRATEGY_FEATURES, self.STRATEGY_TARGETS, self.DIR, self.STRATEGY_RECORD)
        self.STRATEGY_MODEL = self.train(self.STRATEGY_MODEL, self.STRATEGY_FEATURES, self.STRATEGY_TARGETS)
        self.model_save(self.STRATEGY_MODEL, "STRATEGY", self.STRATEGY_FEATURES, self.STRATEGY_TARGETS, self.DIR)        
        
        with open(self.DIR + f"/record_TANK" + '.csv', 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(self.TANK_RECORD)
        self.TANK_RECORD.reverse()
        self.TANK_FEATURES, self.TANK_TARGETS = self.feature_add("TANK", self.TANK_FEATURES, self.TANK_TARGETS, self.DIR, self.TANK_RECORD)
        self.TANK_MODEL = self.train(self.TANK_MODEL, self.TANK_FEATURES, self.TANK_TARGETS)
        self.model_save(self.TANK_MODEL, "TANK", self.TANK_FEATURES, self.TANK_TARGETS, self.DIR)
        if self.GUN_FLAG == True:
            with open(self.DIR + f"/record_GUN" + '.csv', 'w', newline='') as f:
                csv.writer(f, delimiter=',').writerows(self.GUN_RECORD)
            self.GUN_RECORD.reverse()
            self.GUN_FEATURES, self.GUN_TARGETS = self.feature_add("GUN", self.GUN_FEATURES, self.GUN_TARGETS, self.DIR, self.GUN_RECORD)
            self.GUN_MODEL = self.train(self.GUN_MODEL, self.GUN_FEATURES, self.GUN_TARGETS)
            self.model_save(self.GUN_MODEL, "GUN", self.GUN_FEATURES, self.GUN_TARGETS, self.DIR)
        self.GUN_FLAG = False
        self.TANK_FRAME_COUNT = 0
        self.GUN_FRAME_COUNT = 0        

    def model_load(self, model_name, max_depth):
        if not os.path.exists(self.DIR + f"/model_{model_name}.pickle"):
            with open(self.DIR+f"/model_{model_name}.pickle", 'wb') as f:
                pickle.dump(None, f)
                f.flush()
                os.fsync(f.fileno())
            print("-----Creat a New Model-----")
        with open(self.DIR + f"/model_{model_name}.pickle", 'rb') as f:
            try:
                model = pickle.load(f)
            except EOFError:
                pass
        print("-----Model Loaded-----")
        model = DecisionTreeClassifier( max_depth=max_depth,
                                        min_samples_split=2,
                                        min_samples_leaf=1,
                                        max_features=None)
        if os.path.exists(self.DIR + f"/targets_{model_name}.pickle") :
            with open(self.DIR + f"/targets_{model_name}.pickle", 'rb') as f:
                targets = pickle.load(f)     
        if os.path.exists(self.DIR + f"/features_{model_name}.pickle"):
            with open(self.DIR + f"/features_{model_name}.pickle", 'rb') as f:
                features = pickle.load(f)
        if os.path.exists(self.DIR + f"/targets_{model_name}.pickle") and os.path.exists(self.DIR + f"/features_{model_name}.pickle"):
            model.fit(features, targets)
        else:
            print("FIT the model with default parameters")
            if model_name == "STRATEGY":
                model.fit([[0, 0]],[0])
            elif model_name == "TANK":
                model.fit([[0, 0, 0, 0, 0, 0]],[0])
            elif model_name == "GUN":
                model.fit([[0, 0]],[0])

        return model


    def model_save(self, model, model_name, features, targets, DIR):
        if features is not None:
            with open(DIR + f"/features_{model_name}" + '.pickle', 'wb') as f:
                pickle.dump(features, f)
                f.flush()
                os.fsync(f.fileno())
        if targets is not None:
            with open(DIR + f"/targets_{model_name}" + '.pickle', 'wb') as f:
                pickle.dump(targets, f)
                f.flush()
                os.fsync(f.fileno())
        if model is not None:
            with open(DIR+ f"/model_{model_name}" + '.pickle', 'wb') as f:
                pickle.dump(model, f)
                f.flush()
                os.fsync(f.fileno()) 

    def train(self, model, features, targets):

        model.fit(features, targets)

        return model


    def preprocess(self, model, record, scene_info):     

        x1, y1 = scene_info['x'], scene_info['y']        
        oil = scene_info['oil']
        bullet = scene_info['power']
        if model == "STRATEGY":
            feature = [
                oil / 100,
                bullet / 10
            ]
        elif model == "TANK":
            x2, y2 = scene_info[self.object][0]['x'], scene_info[self.object][0]['y']
            angle = scene_info['angle']
            direction = self.get_direction(x1, y1, x2, y2)
            feature = [
                abs(round(x1 % self.WIDTH, 3)), 
                abs(round(y1 % self.HEIGHT, 3)), 
                abs(round(x2 % self.WIDTH, 3)),
                abs(round(y2 % self.HEIGHT, 3)),
                abs(round(angle / 360 , 3)),
                abs(round(direction / 8, 3))
            ]
        elif model == "GUN":
            x2, y2 = scene_info[self.object][0]['x'], scene_info[self.object][0]['y']
            angle = scene_info['gun_angle']
            direction = self.get_direction(x1, y1, x2, y2)
            feature = [
                abs(round(angle / 360 , 3)),
                abs(round(direction / 8, 3))
            ]            

        record.append(feature)

        return feature

    def predict(self, model, feature):
 
        target = model.predict([feature])[0]     

        return target
    
    def feature_add(self, model_name, features, targets, DIR, feature):
   
        if os.path.exists(DIR + f"/targets_{model_name}.pickle") :
            with open(DIR + f"/targets_{model_name}.pickle", 'rb') as f:
                    targets = pickle.load(f)     
        if os.path.exists(DIR + f"/features_{model_name}.pickle"):
            with open(DIR + f"/features_{model_name}.pickle", 'rb') as f:
                    features = pickle.load(f)
        if model_name == "STRATEGY":
            len = self.TANK_FRAME_COUNT + self.GUN_FRAME_COUNT
            for fv in feature[:len]:
                if fv[0]*100 < 50:
                    target = FIND_OIL
                elif fv[1]*10 == 0:
                    target = FIND_BULLET
                else:
                    target = FIND_ENEMY
                features.append(fv)
                targets.append(target)
        elif model_name == "TANK":
            len = self.TANK_FRAME_COUNT   
            for fv in feature[:len]:
                angle = int(fv[4] * 360)
                direction = int(fv[5] * 8)
                target = self.get_target(angle, direction, "TANK")
                features.append(fv)
                targets.append(target)
        elif model_name == "GUN":
            len = self.GUN_FRAME_COUNT        
            for fv in feature[:len]:
                angle = int(fv[0] * 360)
                direction = int(fv[1] * 8)
                target = self.get_target(angle, direction, "GUN")
                features.append(fv)
                targets.append(target)
        print(f"-----{model_name} added {len} features-----")
        return features, targets

    def get_direction(self, x1, y1, x2, y2):
        dx = -(x1 - x2)
        dy = -(y1 - y2)
        if abs(dy) <= 15:
            return ANGLE_0 if dx > 0 else ANGLE_180
        elif abs(dx) <= 15:
            return ANGLE_90 if dy < 0 else ANGLE_270
        else:
            slope = dy / dx
            if slope > 0:
                return ANGLE_315 if dx > 0 else ANGLE_135
            else:
                return ANGLE_45 if dx > 0 else ANGLE_225


    def get_target(self, angle, direction, object):
        target = 0
        if angle < 0 : angle += 360
        if angle == 360 : angle = 0
        
        if direction == ANGLE_0 or direction == ANGLE_180:
            if angle == 180:
                if object == "TANK":
                    target = FORWARD if direction == ANGLE_0 else BACKWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_0 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_180 else False
            elif angle == 0:
                if object == "TANK":
                    target = BACKWARD if direction == ANGLE_0 else FORWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_180 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_0 else False
            elif self.Diagonal and object == "GUN":
                target = AIM_LEFT
            elif angle in [45, 225]:
                    target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
            elif angle in [90, 135, 270, 315]:
                    target = TURN_LEFT if object == "TANK" else AIM_LEFT
        elif direction == ANGLE_90 or direction == ANGLE_270:
            if angle == 90:
                if object == "TANK":
                    target = BACKWARD if direction == ANGLE_90 else FORWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_270 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_90 else False
            elif angle == 270:
                if object == "TANK":
                    target = FORWARD if direction == ANGLE_90 else BACKWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_90 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_270 else False
            elif self.Diagonal and object == "GUN":
                target = AIM_LEFT
            elif angle in [135, 315]:
                target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
            elif angle in [0, 45, 180, 225]:
                target = TURN_LEFT if object == "TANK" else AIM_LEFT
        elif direction == ANGLE_45 or direction == ANGLE_225:
            if angle == 225:
                if object == "TANK":
                    target = FORWARD if direction == ANGLE_45 else BACKWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_45 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_225 else False
            elif angle == 45:
                if object == "TANK":
                    target = BACKWARD if direction == ANGLE_45 else FORWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_225 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_45 else False
            elif self.Diagonal and object == "GUN":
                target = AIM_LEFT
            elif angle in [90, 270]:
                target = TURN_RIGHT if object == "TANK" else AIM_RIGHT                                 
            elif angle in [0, 135, 180, 315]:
                target = TURN_LEFT if object == "TANK" else AIM_LEFT
        elif direction == ANGLE_135 or direction == ANGLE_315:
            if angle == 315:
                if object == "TANK":
                    target = FORWARD if direction == ANGLE_135 else BACKWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_135 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_315 else False
            elif angle == 135:
                if object == "TANK":
                    target = BACKWARD if direction == ANGLE_135 else FORWARD
                elif object == "GUN":
                    target = SHOOT if direction == ANGLE_315 else AIM_LEFT
                    self.Diagonal = True if direction == ANGLE_135 else False
            elif self.Diagonal and object == "GUN":
                target = AIM_LEFT
            elif angle in [0, 180]:
                target = TURN_RIGHT if object == "TANK" else AIM_RIGHT  
            elif angle in [45, 90, 225, 270]:
                target = TURN_LEFT if object == "TANK" else AIM_LEFT
        return target