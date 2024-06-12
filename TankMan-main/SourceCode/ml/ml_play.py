"""
The template of the main script of the machine learning process
"""
from ml.model.utils import get_distance
from ml.model.model import DecisionTreeClassifier_Model
from ml.model.features import feature_add, preprocess
from ml.model.constant import *
import os
import csv
import random
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
        self.STRATEGY_MODEL = DecisionTreeClassifier_Model(f"STRATEGY_{self.side}", self.DIR, 3)
        self.STRATEGY_record = []
        self.TANK_MODEL = DecisionTreeClassifier_Model(f"TANK_{self.side}", self.DIR, max_depth= None)
        self.TANK_record = []
        self.GUN_MODEL = DecisionTreeClassifier_Model(f"GUN_{self.side}", self.DIR, max_depth= None)   
        self.GUN_record = []
        self.object = FIND_ENEMY        
        self.TANK_FRAME_COUNT = 0
        self.GUN_FRAME_COUNT = 0
        self.DONT_MOVE = False
        self.GUN_FLAG = False
        self.Diagonal = False
    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"        
        command = []
        target = ""  
        feature = preprocess("STRATEGY", self.STRATEGY_record, scene_info)
        strategy_num = self.STRATEGY_MODEL.predict(feature)  
        strategy = ["oil_stations_info", "bullet_stations_info", "competitor_info"][strategy_num]
        feature, object = preprocess("TANK", self.TANK_record, scene_info, strategy)
        if self.TANK_MODEL is not None:  
            if random.random() > 0.05 :               
                target = ["TURN_RIGHT", "TURN_LEFT", "FORWARD", "BACKWARD", "DONTMOVE"][self.TANK_MODEL.predict(feature)]
            else:
                target = random.choice(["TURN_RIGHT", "TURN_LEFT", "FORWARD", "BACKWARD"])
        else:
            target = "NONE"
        self.TANK_FRAME_COUNT += 1        
        if target == "DONTMOVE" and object != "bullet_stations_info":
            self.GUN_FLAG = True       
            feature = preprocess("GUN", self.GUN_record, scene_info, object)
            if self.GUN_MODEL is not None:  
                if random.random() > 0.05 :       
                     target = ["SHOOT", "AIM_RIGHT", "AIM_LEFT"][self.GUN_MODEL.predict(feature)]
                else:
                    target = random.choice(["AIM_LEFT", "AIM_RIGHT"])
            else:
                target = "NONE"
            self.GUN_FRAME_COUNT += 1
        command.append(target)
        return command

    def reset(self):
        """
        Reset the status
        """
        print(f"reset Game {self.side}")
        with open(self.DIR + f"/record_STRATEGY_{self.side}" + '.csv', 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(self.STRATEGY_record)
        self.STRATEGY_record.reverse()
        self.STRATEGY_MODEL.features, self.STRATEGY_MODEL.targets, _ = feature_add("STRATEGY", 
                                                                                    self.side,
                                                                                    self.STRATEGY_MODEL.features, 
                                                                                    self.STRATEGY_MODEL.targets, 
                                                                                    self.DIR, 
                                                                                    self.STRATEGY_record,
                                                                                    self.TANK_FRAME_COUNT, 
                                                                                    self.GUN_FRAME_COUNT,
                                                                                    self.Diagonal)
        self.STRATEGY_MODEL.train()
        self.STRATEGY_MODEL.save_model()
        with open(self.DIR + f"/record_TANK_{self.side}" + '.csv', 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(self.TANK_record)
        self.TANK_record.reverse()
        self.TANK_MODEL.features, self.TANK_MODEL.targets, _ = feature_add("TANK",
                                                                        self.side,
                                                                        self.TANK_MODEL.features, 
                                                                        self.TANK_MODEL.targets, 
                                                                        self.DIR, 
                                                                        self.TANK_record,
                                                                        self.TANK_FRAME_COUNT, 
                                                                        self.GUN_FRAME_COUNT,
                                                                        self.Diagonal)
        self.TANK_MODEL.train()
        self.TANK_MODEL.save_model()
        if self.GUN_FLAG == True:
            with open(self.DIR + f"/record_GUN_{self.side}" + '.csv', 'w', newline='') as f:
                csv.writer(f, delimiter=',').writerows(self.GUN_record)
            self.GUN_record.reverse()
            self.GUN_MODEL.features, self.GUN_MODEL.targets, self.Diagonal = feature_add("GUN", 
                                                                                        self.side,
                                                                                        self.GUN_MODEL.features, 
                                                                                        self.GUN_MODEL.targets, 
                                                                                        self.DIR, 
                                                                                        self.GUN_record,
                                                                                        self.TANK_FRAME_COUNT, 
                                                                                        self.GUN_FRAME_COUNT,
                                                                                        self.Diagonal)
            self.GUN_MODEL.train()
            self.GUN_MODEL.save_model()

        self.GUN_FLAG = False
        self.TANK_FRAME_COUNT = 0
        self.GUN_FRAME_COUNT = 0        
