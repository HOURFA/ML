import os
import pickle
from ml.model.utils import *
from ml.model.constant import *
def preprocess(model, record = None, scene_info = None, object = None):     
    x1, y1 = scene_info['x'], scene_info['y']        
    oil = scene_info['oil']
    bullet = scene_info['power']
    x2, y2 = None, None
    wall = None
    is_WALL, is_ENEMY = False, False
    hit_target = False

    if model == "STRATEGY":
        feature = [
            oil / MAX_OIL,
            bullet / MAX_BULLET
        ]
        if record is not None:
            record.append(feature)
        return feature
    elif model == "TANK":
        if object == "competitor_info":
            x2, y2 = scene_info[object][0]['x'], scene_info[object][0]['y']
            is_ENEMY = True
        else:
            x2, y2 = get_nearest_resource(scene_info[object], x1, y1)
        if object != "bullet_stations_info":
            wall = get_closest_wall([x1, y1], [x2, y2], scene_info['walls_info'])
        angle = scene_info['angle']
        direction = get_direction(x1, y1, x2, y2)
        is_WALL = True if wall is not None else False
        object = wall if wall is not None else object
        distance = wall['distance'] if wall is not None else get_distance([x1, y1], [x2, y2])
        wallorenemy = 1 if (is_ENEMY or is_WALL) else 0
        feature = [
            abs(x1 / WIDTH), 
            abs(y1 / HEIGHT), 
            abs(x2 / WIDTH),
            abs(y2 / HEIGHT),
            abs(angle / 360),
            abs(direction / 8),
            abs(distance / MAX_DISTANCE),
            wallorenemy
        ]
        if record is not None:
            record.append(feature)
        return feature, object 
    elif model == "GUN":        
        if object == "competitor_info" or object == "bullet_stations_info" or object == "oil_stations_info":
            x2, y2 = scene_info[object][0]['x'], scene_info[object][0]['y']            
        else:
            x2, y2 = object['x'], object['y']
        angle = scene_info['gun_angle']
        direction = get_direction(x1, y1, x2, y2)
        hit_target = will_hit_target({"x" : x1, "y" : y1}, angle,{"x" : x2, "y" : y2},RADIUS)
        feature = [
            abs(angle / 360),
            abs(direction / 8),
            hit_target
        ]            
        if record is not None:
            record.append(feature)
        return feature
def feature_add(model_name, side, features, targets, DIR, feature,TANK_FRAME_COUNT, GUN_FRAME_COUNT, Diagonal):
    if os.path.exists(DIR + f"/targets_{model_name}_{side}.pickle"):
        with open(DIR + f"/targets_{model_name}_{side}.pickle", 'rb') as f:
            targets = pickle.load(f)     
    if os.path.exists(DIR + f"/features_{model_name}_{side}.pickle"):
        with open(DIR + f"/features_{model_name}_{side}.pickle", 'rb') as f:
            features = pickle.load(f)

    if model_name == "STRATEGY":
        len = TANK_FRAME_COUNT
        for fv in feature[:len]:
            if int(fv[0]*100) < 50:
                target = FIND_OIL
            elif int(fv[1]*10) <= 3:
                target = FIND_BULLET
            else:
                target = FIND_ENEMY
            features.append(fv)
            targets.append(target)
    elif model_name == "TANK":
        len = TANK_FRAME_COUNT   
        for fv in feature[:len]:
            angle = int(fv[4] * 360)
            direction = int(fv[5] * 8)
            disance = int(fv[6] * MAX_DISTANCE)
            wallorenemy = fv[7]
            target, _ = get_target(angle, direction, "TANK", Diagonal, disance, wallorenemy)
            features.append(fv)
            targets.append(target)
    elif model_name == "GUN":
        len = GUN_FRAME_COUNT        
        for fv in feature[:len]:
            angle = int(fv[0] * 360)
            direction = int(fv[1] * 8)
            hit_target = fv[2]
            target, Diagonal = get_target(angle, direction, "GUN", Diagonal, hit_target = hit_target)
            features.append(fv)
            targets.append(target)
    print(f"-----{model_name} added {len} features-----")
    return features, targets, Diagonal

def get_target(angle, direction, object, Diagonal=False, distance = MAX_DISTANCE, wallorenemy = 0, hit_target = False):
    target = 0
    if object == "TANK":
        if wallorenemy == 1 and distance <= RADIUS: 
            return DONTMOVE, Diagonal
    elif object == "GUN":
        if hit_target:
            return SHOOT, Diagonal
    if angle < 0 : angle += 360
    if angle == 360 : angle = 0

    if direction == ANGLE_0 or direction == ANGLE_180:
        if angle == 180:
            if object == "TANK":
                target = FORWARD if direction == ANGLE_0 else BACKWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_0 else AIM_LEFT
                Diagonal = True if direction == ANGLE_180 else False
        elif angle == 0:
            if object == "TANK":
                target = BACKWARD if direction == ANGLE_0 else FORWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_180 else AIM_LEFT
                Diagonal = True if direction == ANGLE_0 else False
        elif Diagonal and object == "GUN":
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
                Diagonal = True if direction == ANGLE_90 else False
        elif angle == 270:
            if object == "TANK":
                target = FORWARD if direction == ANGLE_90 else BACKWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_90 else AIM_LEFT
                Diagonal = True if direction == ANGLE_270 else False
        elif Diagonal and object == "GUN":
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
                Diagonal = True if direction == ANGLE_225 else False
        elif angle == 45:
            if object == "TANK":
                target = BACKWARD if direction == ANGLE_45 else FORWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_225 else AIM_LEFT
                Diagonal = True if direction == ANGLE_45 else False
        elif Diagonal and object == "GUN":
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
                Diagonal = True if direction == ANGLE_315 else False
        elif angle == 135:
            if object == "TANK":
                target = BACKWARD if direction == ANGLE_135 else FORWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_315 else AIM_LEFT
                Diagonal = True if direction == ANGLE_135 else False
        elif Diagonal and object == "GUN":
            target = AIM_LEFT
        elif angle in [0, 180]:
            target = TURN_RIGHT if object == "TANK" else AIM_RIGHT  
        elif angle in [45, 90, 225, 270]:
            target = TURN_LEFT if object == "TANK" else AIM_LEFT
    return target, Diagonal