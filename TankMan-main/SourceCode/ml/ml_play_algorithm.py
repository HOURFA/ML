"""
The template of the main script of the machine learning process
"""
import random
import math


TURN_RIGHT = 0
TURN_LEFT = 1
FORWARD = 2
BACKWARD = 3
SHOOT = 4
AIM_RIGHT = 0
AIM_LEFT = 1


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
            self.FIND_OIL = True
        else:
            self.FIND_OIL = False            
        feature = self.preprocess(scene_info)
        direction = feature[5] * 8
        angle = int(feature[4] * 360)
        target = self.get_target(angle, direction, "TANK")
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

    def preprocess(self, scene_info):
        """
        Preprocesses the scene information and returns a feature vector.

        Args:
            scene_info (dict): A dictionary containing the scene information.

        Returns:
            list: A feature vector containing the preprocessed information.

        """        
        x, y = scene_info['x'], scene_info['y']
        if self.FIND_OIL:
            object = "oil_stations_info"    
        else:
            object = "bullet_stations_info"        
        x2, y2 = scene_info[object][0]['x'], scene_info[object][0]['y']
        angle = scene_info['angle']
        direction = self.get_direction(x, y, x2, y2)      
        feature = [x / self.WIDTH, 
                   y / self.HEIGHT, 
                   x2 / self.WIDTH,
                   y2 / self.HEIGHT,
                   angle / 360,
                   direction / 8
                   ]        

        return feature
    
    def get_direction(self, x1, y1, x2, y2):
        dx = -(x1 - x2)
        dy = -(y1 - y2)
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        self.DONT_MOVE = True if distance <= RADIUS else False
        
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
        # print(angle, direction, target)
        return target