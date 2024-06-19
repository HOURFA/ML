import math
from shapely.geometry import LineString, Polygon
from ml.model.constant import *
import numpy as np
import math

def get_nearest_resource(resources, x1, y1):
    """
    Finds the nearest resource from a given list of resources based on the distance.

    Parameters:
    resources (list): A list of dictionaries representing the resources, where each dictionary contains 'x' and 'y' coordinates.
    x1 (float): The x-coordinate of the reference point.
    y1 (float): The y-coordinate of the reference point.

    Returns:
    tuple: A tuple containing the x and y coordinates of the nearest resource.
    """
    nearest_resource = min(resources, key=lambda r: math.sqrt((r['x'] - x1)**2 + (r['y'] - y1)**2))
    return nearest_resource['x'], nearest_resource['y']

def get_direction(x1, y1, x2, y2):
    """
    Calculates the direction angle between two points (x1, y1) and (x2, y2).

    Args:
        x1 (float): The x-coordinate of the first point.
        y1 (float): The y-coordinate of the first point.
        x2 (float): The x-coordinate of the second point.
        y2 (float): The y-coordinate of the second point.

    Returns:
        float: Encoded direction angle.

    """
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


def get_closest_wall(source_pos, target_pos, walls):
    """
    Check for the closest wall on the path from source to target.

    Args:
        source_pos (tuple): The position of the source point.
        target_pos (tuple): The position of the target point.
        walls (list): A list of wall objects.

    Returns:
        dict or None: The closest wall object if found, otherwise None.
    """
    show = False
    min_distance = float('inf')
    closest_wall = None
    path_line = LineString([source_pos, target_pos])
    path_length = path_line.length

    for wall in walls:
        if wall['y'] != 0 and wall['y'] != HEIGHT and wall['x'] != 0 and wall['x'] != WIDTH:
            wall_pos = (wall['x'], wall['y'])
            wall_rect = get_wall_rect(wall_pos)
            if path_line.intersects(wall_rect):
                intersection = path_line.intersection(wall_rect)
                if not intersection.is_empty:
                    intersection_point = intersection.centroid
                    distance_on_path = path_line.project(intersection_point)
                    if 0 <= distance_on_path <= path_length:
                        distance = get_distance(source_pos, wall_pos)
                        if distance < min_distance:
                            min_distance = distance
                            closest_wall = wall

    if closest_wall is not None:
        closest_wall['distance'] = min_distance
    if show:
        import cv2
        import numpy as np
        img = np.zeros((600, 1000, 3), dtype=np.uint8)

        cv2.line(img, (source_pos[0], source_pos[1]), (target_pos[0], target_pos[1]), (255, 0, 0), 2)

        cv2.circle(img, (source_pos[0], source_pos[1]), 10, (0, 0, 255), -1)
        cv2.circle(img, (target_pos[0], target_pos[1]), 10, (0, 255, 0), -1)

        for wall in walls:
            wall_pos = (wall['x'], wall['y'])
            wall_rect = get_wall_rect(wall_pos)
            x, y = wall_rect.exterior.xy
            cv2.fillPoly(img, [np.array([(x[i], y[i]) for i in range(len(x))], dtype=np.int32)], (255, 255, 255))

        if closest_wall is not None:
            wall_pos = (closest_wall['x'], closest_wall['y'])
            wall_rect = get_wall_rect(wall_pos)
            x, y = wall_rect.exterior.xy
            cv2.fillPoly(img, [np.array([(x[i], y[i]) for i in range(len(x))], dtype=np.int32)], (0, 0, 255))

        cv2.imshow('Image', img)
        cv2.waitKey(1)

    return closest_wall

def get_wall_rect(wall_pos, wall_width=30, wall_height=30):
    """
    Create a rectangle polygon for the wall given its position and dimensions.
    """
    x, y = wall_pos
    rect = Polygon([
        (x, y),
        (x + wall_width, y),
        (x + wall_width, y + wall_height),
        (x, y + wall_height)
    ])
    return rect

def get_distance(source, target):
    """
    Calculate the distance between two points.

    Parameters:
    source (tuple): The coordinates of the source point (x, y).
    target (tuple): The coordinates of the target point (x, y).

    Returns:
    float: The distance between the source and target points.
    """
    return math.sqrt((target[0] - source[0])**2 + (target[1] - source[1])**2)


def will_hit_target(tank_pos, gun_angle, target_pos, detection_distance):
    """
    Determines whether the tank's gun will hit the target based on the tank's position, gun angle, target position, and detection distance.

    Parameters:
    tank_pos (dict): A dictionary containing the x and y coordinates of the tank's position.
    gun_angle (float): The angle of the tank's gun in degrees.
    target_pos (dict): A dictionary containing the x and y coordinates of the target's position.
    detection_distance (float): The maximum distance at which the tank can detect the target.

    Returns:
    bool: True if the tank's gun will hit the target, False otherwise.
    """
    distance = math.sqrt((tank_pos["x"] - target_pos["x"]) ** 2 + (tank_pos["y"] - target_pos["y"]) **2)
    
    if detection_distance < distance:
        return False
    
    angle_rad = math.atan2(target_pos["y"] - tank_pos["y"], target_pos["x"] - tank_pos["x"])            
    gun_rad = np.radians(180 - gun_angle) 
    toarance_rad = math.atan2((WALL_WIDTH)/2, distance)
    
    return abs(gun_rad - angle_rad) < toarance_rad