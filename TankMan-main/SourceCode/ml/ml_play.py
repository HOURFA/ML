"""
The template of the main script of the machine learning process
"""
from ml.model.model import DecisionTreeClassifier_Model
from ml.model.features import feature_add, preprocess
from ml.model.constant import *
import os
import csv
import random
dir_path_extend = ""
class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        print(f"Initial Game {ai_name} ml script",flush=True)
        self.side = ai_name
        self.DIR = os.path.dirname(__file__) + dir_path_extend        
        self.STRATEGY_MODEL = DecisionTreeClassifier_Model(f"STRATEGY_{self.side}", self.DIR, 3)
        self.STRATEGY_record = []
        self.TANK_MODEL = DecisionTreeClassifier_Model(f"TANK_{self.side}", self.DIR, max_depth= None)
        self.TANK_record = []
        self.GUN_MODEL = DecisionTreeClassifier_Model(f"GUN_{self.side}", self.DIR, max_depth= None)   
        self.GUN_record = []
        self.TANK_FRAME_COUNT = 0
        self.GUN_FRAME_COUNT = 0
        self.GUN_FLAG = False
        self.Diagonal = False
        self.DEBUG = False
        self.train = True
    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"        
        command = []
        target = ""  
        feature = preprocess("STRATEGY", scene_info=scene_info, record=self.STRATEGY_record)
        strategy_num = self.STRATEGY_MODEL.predict(feature)  
        strategy = ["oil_stations_info", "bullet_stations_info", "competitor_info"][int(strategy_num)]
        feature, object = preprocess("TANK",scene_info=scene_info, record=self.TANK_record, object=strategy)
        if self.TANK_MODEL is not None:  
            if random.random() > 0.05 :               
                target = ["TURN_RIGHT", "TURN_LEFT", "FORWARD", "BACKWARD", "DONTMOVE"][int(self.TANK_MODEL.predict(feature))]
            else:
                target = random.choice(["TURN_RIGHT", "TURN_LEFT", "FORWARD", "BACKWARD"])
        else:
            target = "NONE"
        self.TANK_FRAME_COUNT += 1        
        if target == "DONTMOVE":
            self.GUN_FLAG = True       
            feature = preprocess("GUN", scene_info=scene_info, record=self.GUN_record, object = object)
            if self.GUN_MODEL is not None:  
                if random.random() > 0.05 :       
                     target = ["SHOOT", "AIM_RIGHT", "AIM_LEFT"][int(self.GUN_MODEL.predict(feature))]
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
        print(f"reset Game {self.side}",flush=True)
        if self.train:
            with open(self.DIR + f"/record_STRATEGY_{self.side}" + '.csv', 'w', newline='') as f:
                csv.writer(f, delimiter=',').writerows(self.STRATEGY_record)
            self.STRATEGY_record.reverse()
            _, _= feature_add("STRATEGY", 
                            self.STRATEGY_MODEL,
                            self.STRATEGY_record,
                            self.TANK_FRAME_COUNT)
            self.STRATEGY_MODEL.train()
            self.STRATEGY_MODEL.save_model()
            with open(self.DIR + f"/record_TANK_{self.side}" + '.csv', 'w', newline='') as f:
                csv.writer(f, delimiter=',').writerows(self.TANK_record)
            self.TANK_record.reverse()
            _, self.DEBUG = feature_add("TANK",
                                        self.TANK_MODEL,
                                        self.TANK_record,
                                        self.TANK_FRAME_COUNT,
                                        DEBUG = self.DEBUG)
            self.TANK_MODEL.train()
            self.TANK_MODEL.save_model()
            if self.GUN_FLAG == True:
                with open(self.DIR + f"/record_GUN_{self.side}" + '.csv', 'w', newline='') as f:
                    csv.writer(f, delimiter=',').writerows(self.GUN_record)
                self.GUN_record.reverse()
                self.Diagonal, self.DEBUG = feature_add("GUN",
                                                        self.GUN_MODEL,
                                                        self.GUN_record,
                                                        self.GUN_FRAME_COUNT,
                                                        self.Diagonal,
                                                        self.DEBUG)
                self.GUN_MODEL.train()
                self.GUN_MODEL.save_model()

        self.GUN_FLAG = False
        self.TANK_FRAME_COUNT = 0
        self.GUN_FRAME_COUNT = 0        
