"""
The template of the main script of the machine learning process
"""
from ml.model.constant import *
from ml.model.features import *
#python -m mlgame -f 30 -i ./ml/ml_play_algorithm.py -i ./ml/ml_play_algorithm.py . --green_team_num 1 --blue_team_num 1 --frame_limit 1000 --is_manual "" --sound off
class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        print(f"Initial Game {ai_name} ml script")
        self.side = ai_name        
        self.DIR = os.path.dirname(__file__)
        self.Diagonal = False
        self.DEBUG = False
    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """        
        if scene_info["status"] != "GAME_ALIVE":            
            return "RESET"      
        command = []
        feature = preprocess(model = "STRATEGY", scene_info = scene_info)
        if int(feature[0]*100) < 50:
            STRATEGY_targets = FIND_OIL
        elif int(feature[1]*10) <= 3:
            STRATEGY_targets = FIND_BULLET
        else:
            STRATEGY_targets = FIND_ENEMY             
        strategy = ["oil_stations_info", "bullet_stations_info", "competitor_info"][int(STRATEGY_targets)]
        feature,object = preprocess(model = "TANK", scene_info = scene_info, object = strategy)
        x1 = int(feature[0] * WIDTH)
        y1 = int(feature[1] * HEIGHT)
        x2 = int(feature[2] * WIDTH)
        y2 = int(feature[3] * HEIGHT)
        if abs(x1) < WIDTH and abs(y1) < HEIGHT and abs(x2) < WIDTH and abs(y2) < HEIGHT:
            angle = int(feature[4] * 360)
            direction = int(feature[5] * 8)
            disance = int(feature[6] * MAX_DISTANCE)
            wallorenemy = feature[7]                              
            hit_target = will_hit_target({"x" : x1, "y" : y1}, angle,{"x" : x2, "y" : y2},RADIUS) if wallorenemy == 1 else False
            TANK_targets,_, self.DEBUG = get_target(angle, direction, "TANK", distance=disance, wallorenemy=wallorenemy, hit_target=hit_target, source = [x1, y1], destination = [x2, y2], DEBUG = self.DEBUG)                       
        target = ["TURN_RIGHT", "TURN_LEFT", "FORWARD", "BACKWARD", "DONTMOVE"][int(TANK_targets)]
        if target == "DONTMOVE":
            feature = preprocess(model = "GUN", scene_info = scene_info, object = object)
            angle = int(feature[0] * 360)
            direction = int(feature[1] * 8)
            GUN_targets, self.Diagonal, _ = get_target(angle, direction, "GUN", Diagonal = self.Diagonal)
            target = ["SHOOT", "AIM_RIGHT", "AIM_LEFT"][int(GUN_targets)]
        command.append(target)
        return command

    def reset(self):
        """
        Reset the status
        """
        print(f"reset Game {self.side}")