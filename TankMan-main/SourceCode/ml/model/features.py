import os
import pickle
from ml.model.utils import *
from ml.model.constant import *
def preprocess(model, scene_info,record = None, object=None):
    """
    Preprocesses the input data based on the specified model.

    Args:
        model (str): The model to preprocess the data for. Possible values are "STRATEGY", "TANK", or "GUN".
        record (list): A list to store the preprocessed features.
        scene_info (dict): The scene information dictionary.
        object (str, optional): The object to preprocess the data for. Defaults to None.

    Returns:
        list: The preprocessed features based on the specified model and object.
              If the model is "STRATEGY" or "GUN", returns a list of features.
              If the model is "TANK", returns a list of features and the object.

    """
    x1, y1 = scene_info['x'], scene_info['y']        
    oil = scene_info['oil']
    bullet = scene_info['power']
    x2, y2 = None, None
    wall = None
    is_WALL, is_ENEMY = False, False
    feature = []
    if model == "STRATEGY":
        feature = [
            abs(round(oil / MAX_OIL, 3)),
            abs(round(bullet / MAX_BULLET, 3))
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
        wall = get_closest_wall([x1 , y1], [x2 , y2], scene_info['walls_info'])        
        angle = scene_info['angle']
        if wall is not None:
            x2, y2 = wall['x'], wall['y']
            is_WALL = True
            object = wall
            distance = wall['distance'] 
        else:
            is_WALL = False
            object = object
            distance = get_distance([x1, y1], [x2, y2])
        direction = get_direction(x1, y1, x2, y2)            
        wallorenemy = 1 if (is_ENEMY or is_WALL) else 0
        feature = [
            abs(round(x1 / WIDTH, 3)), 
            abs(round(y1 / HEIGHT, 3)), 
            abs(round(x2 / WIDTH, 3)),
            abs(round(y2 / HEIGHT, 3)),
            abs(round(angle / 360, 3)),
            abs(round(direction / 8, 3)),
            abs(round(distance / MAX_DISTANCE, 3)),
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
        feature = [
            abs(round(angle / 360, 3)),
            abs(round(direction / 8, 3))
        ]
        if record is not None:
            record.append(feature)
        return feature
def feature_add(model_name, model, feature, FRAME_COUNT, Diagonal=None, DEBUG=None):
    """
    Add features to the given feature list based on the model name.

    Args:
        model_name (str): The name of the model.
        model (object): The model object.
        feature (list): The list of features to be added.
        FRAME_COUNT (int): The number of frames.
        Diagonal (bool, optional): The diagonal flag. Defaults to None.
        DEBUG (bool, optional): The debug flag. Defaults to None.

    Returns:
        tuple: A tuple containing the Diagonal, and DEBUG values.
    """
    model.load_data()
    if model_name == "STRATEGY":
        for fv in feature[:FRAME_COUNT]:
            if int(fv[0] * 100) < 50:
                target = FIND_OIL
            elif int(fv[1] * 10) <= 3:
                target = FIND_BULLET
            else:
                target = FIND_ENEMY
            model.features.append(fv)
            model.targets.append(target)
    elif model_name == "TANK":
        for fv in feature[:FRAME_COUNT]:
            x1 = int(fv[0] * WIDTH)
            y1 = int(fv[1] * HEIGHT)
            x2 = int(fv[2] * WIDTH)
            y2 = int(fv[3] * HEIGHT)
            if abs(x1) < WIDTH and abs(y1) < HEIGHT and abs(x2) < WIDTH and abs(y2) < HEIGHT:
                angle = int(fv[4] * 360)
                direction = int(fv[5] * 8)
                distance = int(fv[6] * MAX_DISTANCE)
                wallorenemy = fv[7]
                hit_target = will_hit_target({"x": x1, "y": y1}, angle, {"x": x2, "y": y2}, RADIUS) if wallorenemy == 1 else False
                target, _, DEBUG = get_target(angle, direction, "TANK", distance = distance, wallorenemy = wallorenemy, hit_target = hit_target, source=[x1, y1], destination=[x2, y2], DEBUG=DEBUG)
                model.features.append(fv)
                model.targets.append(target)
    elif model_name == "GUN":
        for fv in feature[:FRAME_COUNT]:            
            angle = int(fv[0] * 360)
            direction = int(fv[1] * 8)
            target, Diagonal, DEBUG = get_target(angle, direction, "GUN", Diagonal=Diagonal, DEBUG=DEBUG)
            model.features.append(fv)
            model.targets.append(target)
    print(f"-----{model_name} added {FRAME_COUNT} features-----")
    return Diagonal, DEBUG

def get_target(angle, direction, object, Diagonal=False, distance=MAX_DISTANCE, wallorenemy=0, hit_target=False, source=None, destination=None, DEBUG=None):
    """
    Determines the target action based on the given parameters.

    Args:
        angle (float): The angle of the target.
        direction (int): The direction of the target.
        object (str): The object type ('TANK' or 'GUN').
        Diagonal (bool, optional): Indicates if the target is diagonal. Defaults to False.
        distance (float, optional): The distance to the target. Defaults to MAX_DISTANCE.
        wallorenemy (int, optional): Indicates if the target is a wall or an enemy. Defaults to 0.
        hit_target (bool, optional): Indicates if the target has been hit. Defaults to False.
        source (tuple, optional): The source coordinates. Defaults to None.
        destination (tuple, optional): The destination coordinates. Defaults to None.
        DEBUG (bool, optional): Indicates if debug mode is enabled. Defaults to None.

    Returns:
        tuple: The target action, diagonal flag, and debug flag.
    """
    angle = angle % 360
    if object == "TANK":
        if wallorenemy == 1 and distance <= RADIUS:
            if hit_target:
                return DONTMOVE, Diagonal, DEBUG
            else:
                if direction in [ANGLE_0, ANGLE_180]:
                    if angle == 90 or angle == 270:
                        DEBUG = False
                        if source[1] > destination[1]:
                            target = FORWARD if angle == 270 else BACKWARD
                        else:
                            target = BACKWARD if angle == 270 else FORWARD
                    else:
                        if angle in [45, 225]:
                            target = TURN_LEFT
                            DEBUG = True
                        elif angle in [0, 135, 180, 315]:
                            target = TURN_RIGHT if not DEBUG else TURN_LEFT
                elif direction in [ANGLE_90, ANGLE_270]:
                    if angle == 0 or angle == 180:
                        if source[0] < destination[0]:
                            DEBUG = False
                            target = FORWARD if angle == 0 else BACKWARD
                        else:
                            target = BACKWARD if angle == 0 else FORWARD
                    else:
                        if angle in [135, 315]:
                            target = TURN_LEFT
                            DEBUG = True
                        elif angle in [45, 90, 225, 270]:
                            target = TURN_RIGHT if not DEBUG else TURN_LEFT
                elif direction in [ANGLE_45, ANGLE_225]:
                    if angle == 135 or angle == 315:
                        slope = (destination[1] - source[1]) / (destination[0] - source[0] + 0.0001)
                        DEBUG = False
                        if source[0] < destination[0]:
                            if slope > 1:
                                target = FORWARD if angle == 135 else BACKWARD
                            else:
                                target = BACKWARD if angle == 135 else FORWARD
                        else:
                            if slope < 1:
                                target = FORWARD if angle == 135 else BACKWARD
                            else:
                                target = BACKWARD if angle == 135 else FORWARD
                    else:
                        if angle in [90, 270]:
                            target = TURN_LEFT
                            DEBUG = True
                        elif angle in [0, 45, 180, 225]:
                            target = TURN_RIGHT if not DEBUG else TURN_LEFT
                elif direction in [ANGLE_135, ANGLE_315]:
                    if angle == 45 or angle == 225:
                        slope = (destination[1] - source[1]) / (destination[0] - source[0] + 0.0001)
                        DEBUG = False
                        if source[0] > destination[0]:
                            if slope > -1:
                                target = FORWARD if angle == 315 else BACKWARD
                            else:
                                target = BACKWARD if angle == 315 else FORWARD
                        else:
                            if slope < -1:
                                target = FORWARD if angle == 315 else BACKWARD
                            else:
                                target = BACKWARD if angle == 315 else FORWARD
                    else:
                        if angle in [0, 135, 180, 315]:
                            target = TURN_LEFT
                            DEBUG = True
                        elif angle in [90, 270]:
                            target = TURN_RIGHT if not DEBUG else TURN_LEFT
                cheack_hit_target_a = will_hit_target({"x": source[0], "y": source[1]}, angle + 90,
                                                      {"x": destination[0], "y": destination[1]}, RADIUS)
                cheack_hit_target_b = will_hit_target({"x": source[0], "y": source[1]}, angle - 90,
                                                      {"x": destination[0], "y": destination[1]}, RADIUS)
                target = DONTMOVE if (cheack_hit_target_a or cheack_hit_target_b) else target
            return target, Diagonal, DEBUG
    if direction == ANGLE_0 or direction == ANGLE_180:
        if angle == 180:
            DEBUG = False
            if object == "TANK":
                target = FORWARD if direction == ANGLE_0 else BACKWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_0 else AIM_LEFT
                Diagonal = True if direction == ANGLE_180 else False
        elif angle == 0:
            DEBUG = False
            if object == "TANK":
                target = BACKWARD if direction == ANGLE_0 else FORWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_180 else AIM_LEFT
                Diagonal = True if direction == ANGLE_0 else False
        elif Diagonal and object == "GUN":
            target = AIM_LEFT
        elif angle in [45, 225]:
            target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
            DEBUG = True
        elif angle in [90, 135, 270, 315]:
            target = TURN_LEFT if object == "TANK" else AIM_LEFT
            if DEBUG:
                target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
    elif direction == ANGLE_90 or direction == ANGLE_270:
        if angle == 90:
            DEBUG = False
            if object == "TANK":
                target = BACKWARD if direction == ANGLE_90 else FORWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_270 else AIM_LEFT
                Diagonal = True if direction == ANGLE_90 else False
        elif angle == 270:
            DEBUG = False
            if object == "TANK":
                target = FORWARD if direction == ANGLE_90 else BACKWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_90 else AIM_LEFT
                Diagonal = True if direction == ANGLE_270 else False
        elif Diagonal and object == "GUN":
            target = AIM_LEFT
        elif angle in [135, 315]:
            target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
            DEBUG = True
        elif angle in [0, 45, 180, 225]:
            target = TURN_LEFT if object == "TANK" else AIM_LEFT
            if DEBUG:
                target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
    elif direction == ANGLE_45 or direction == ANGLE_225:
        if angle == 225:
            DEBUG = False
            if object == "TANK":
                target = FORWARD if direction == ANGLE_45 else BACKWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_45 else AIM_LEFT
                Diagonal = True if direction == ANGLE_225 else False
        elif angle == 45:
            DEBUG = False
            if object == "TANK":
                target = BACKWARD if direction == ANGLE_45 else FORWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_225 else AIM_LEFT
                Diagonal = True if direction == ANGLE_45 else False
        elif Diagonal and object == "GUN":
            target = AIM_LEFT
        elif angle in [90, 270]:
            target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
            DEBUG = True
        elif angle in [0, 135, 180, 315]:
            target = TURN_LEFT if object == "TANK" else AIM_LEFT
            if DEBUG:
                target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
    elif direction == ANGLE_135 or direction == ANGLE_315:
        if angle == 315:
            DEBUG = False
            if object == "TANK":
                target = FORWARD if direction == ANGLE_135 else BACKWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_135 else AIM_LEFT
                Diagonal = True if direction == ANGLE_315 else False
        elif angle == 135:
            DEBUG = False
            if object == "TANK":
                target = BACKWARD if direction == ANGLE_135 else FORWARD
            elif object == "GUN":
                target = SHOOT if direction == ANGLE_315 else AIM_LEFT
                Diagonal = True if direction == ANGLE_135 else False
        elif Diagonal and object == "GUN":
            target = AIM_LEFT
        elif angle in [0, 180]:
            target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
            DEBUG = True
        elif angle in [45, 90, 225, 270]:
            target = TURN_LEFT if object == "TANK" else AIM_LEFT
            if DEBUG:
                target = TURN_RIGHT if object == "TANK" else AIM_RIGHT
    return target, Diagonal, DEBUG