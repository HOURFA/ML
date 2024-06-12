import math
from shapely.geometry import LineString, Point, Polygon
from ml.model.constant import *
import numpy as np
def get_nearest_resource(resources, x1, y1):
        nearest_resource = min(resources, key=lambda r: math.sqrt((r['x'] - x1)**2 + (r['y'] - y1)**2))
        return nearest_resource['x'], nearest_resource['y']

def get_direction(x1, y1, x2, y2):
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
    """
    show = False
    min_distance = float('inf')
    closest_wall = None
    path_line = LineString([source_pos, target_pos])

    for wall in walls:
        wall_pos = (wall['x'], wall['y'])
        wall_rect = get_wall_rect(wall_pos)
        if path_line.intersects(wall_rect):
            distance = get_distance(source_pos, wall_pos)
            if distance < min_distance:
                min_distance = distance
                closest_wall = wall

    if closest_wall is not None:
        closest_wall['distance'] = min_distance
    if show:
        import cv2
        import numpy as np
        # Create a blank image
        img = np.zeros((600, 1000, 3), dtype=np.uint8)

        # Draw the path line
        cv2.line(img, (source_pos[0], source_pos[1]), (target_pos[0], target_pos[1]), (255, 0, 0), 2)

        # Draw the source and target points
        cv2.circle(img, (source_pos[0], source_pos[1]), 10, (0, 0, 255), -1)
        cv2.circle(img, (target_pos[0], target_pos[1]), 10, (0, 255, 0), -1)

        # Draw the walls
        for wall in walls:
            wall_pos = (wall['x'], wall['y'])
            wall_rect = get_wall_rect(wall_pos)
            x, y = wall_rect.exterior.xy
            cv2.fillPoly(img, [np.array([(x[i], y[i]) for i in range(len(x))], dtype=np.int32)], (255, 255, 255))

        # Draw the closest wall
        if closest_wall is not None:
            wall_pos = (closest_wall['x'], closest_wall['y'])
            wall_rect = get_wall_rect(wall_pos)
            x, y = wall_rect.exterior.xy
            cv2.fillPoly(img, [np.array([(x[i], y[i]) for i in range(len(x))], dtype=np.int32)], (0, 0, 255))

        # Display the image
        cv2.imshow('Image', img)
        cv2.waitKey(1)

    return closest_wall

def get_wall_rect(wall_pos, wall_width=25, wall_height=25):
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

    return math.sqrt((target[0] - source[0])**2 + (target[1] - source[1])**2)
def will_hit_target(tank_pos, gun_angle, target_pos, detection_distance):    
    distance = math.sqrt((tank_pos["x"] - target_pos["x"]) ** 2 + (tank_pos["y"] - target_pos["y"]) **2)
    
    if detection_distance < distance:
        return False
    
    angle_rad = math.atan2(target_pos["y"] - tank_pos["y"], target_pos["x"] - tank_pos["x"])            
    gun_rad = np.radians(180 - gun_angle) 
    toarance_rad = math.atan2(WALL_WIDTH/2, distance)
    
    
    return abs(gun_rad - angle_rad) < toarance_rad