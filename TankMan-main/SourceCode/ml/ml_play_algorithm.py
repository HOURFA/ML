"""
The template of the main script of the machine learning process
"""
import random
import math
from ml.model.constant import *
from ml.model.utils import get_direction, get_nearest_resource
from ml.model.features import get_target,preprocess



class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.side = ai_name
        print(f"Initial Game {ai_name} ml script")
        self.time = 0
        self.WIDTH = 1000
        self.HEIGHT = 600  
        self.FIND_OIL = False
        self.Diagonal = False
    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """        
        if scene_info["status"] != "GAME_ALIVE":            
            return "RESET"      
        command = []
        oil = scene_info['oil']
        if oil < 50:
            object = "oil_stations_info"

        else:
            object = "bullet_stations_info"
        feature,_ = preprocess(model = "TANK", scene_info = scene_info, object = object)
        direction = feature[5] * 8
        angle = int(feature[4] * 360)
        target,_ = get_target(angle, direction, "TANK")
        if random.random() > 0.05:   
            if   target == TURN_RIGHT : command.append("TURN_RIGHT")
            elif target == TURN_LEFT : command.append("TURN_LEFT")
            elif target == FORWARD : command.append("FORWARD")
            elif target == BACKWARD : command.append("BACKWARD")
        else: command.append(random.choice(["TURN_RIGHT", "TURN_LEFT", "FORWARD", "BACKWARD"]))

        
        return command

    def reset(self):
        """
        Reset the status
        """
        print(f"reset Game {self.side}")
        self.FIND_OIL = False