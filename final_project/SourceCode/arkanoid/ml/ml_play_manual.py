"""
The template of the main script of the machine learning process
"""
import pygame
import numpy as np
from ML_model import QTable

class MLPlay:
    def __init__(self,ai_name, *args, **kwargs):
        """
        Constructor
        """
        self.ball_served = False

        self.q_learning_model = QTable()  # Create a QTable instance

    def update(self, scene_info, keyboard=None, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        # Make the caller to invoke `reset()` for the next round.
        ball_x = scene_info["ball"][0]
        ball_y = scene_info["ball"][1]
        platform_x = scene_info["platform"][0]
        distance = abs(ball_x - platform_x)
        command = "NONE"
        # if keyboard is None:
        #     keyboard = []
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            return "RESET"
        elif not scene_info["ball_served"]:                
            if pygame.K_q in keyboard:
                command = "SERVE_TO_LEFT"
                self.ball_served = True
            elif pygame.K_e in keyboard:
                command = "SERVE_TO_RIGHT"
                self.ball_served = True 
        else:
            if pygame.K_LEFT in keyboard or pygame.K_a in keyboard:            
                command = "MOVE_LEFT"
            elif pygame.K_RIGHT in keyboard or pygame.K_d in keyboard:
                command = "MOVE_RIGHT"
            else:
                command = "NONE"

            if abs(ball_y) > 200:
                reward = (100 - distance) / 50
            else:
                reward = (100 - distance) / 100

            feature = np.array([ball_x, ball_y, platform_x])
            self.q_learning_model.augment(feature, command, reward,5)
            # self.q_learning_model.update(feature, command, reward)            

        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
        self.q_learning_model.save_table("Q_learning_model.npy")
