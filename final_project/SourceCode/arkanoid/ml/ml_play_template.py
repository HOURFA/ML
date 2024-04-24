from ML_model import QTable
import numpy as np
import time
"""
The template of the main script of the machine learning process
"""


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor
        """
        print(ai_name)

        self.q_learning_model = QTable()  # Create a QTable instance

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        ball_x = scene_info["ball"][0]
        ball_y = scene_info["ball"][1]
        platform_x = scene_info["platform"][0]        
        # Make the caller invoke `reset()` for the next round.
        if scene_info["status"] == "GAME_OVER" or scene_info["status"] == "GAME_PASS":
            return "RESET"

        feature = np.array([ball_x, ball_y, platform_x])           
        # Use the prediction to generate the command        
        if not scene_info["ball_served"]:
            command = np.random.choice(["SERVE_TO_LEFT", "SERVE_TO_RIGHT"])            
        else:
            start_time = time.time()
            command = self.q_learning_model.predict(feature)
            # print(f"time: {time.time()-start_time}",)
            distance = abs(ball_x - platform_x)
            if abs(ball_y) > 200:
                reward = (100 - distance) / 50
            else:
                reward = (100 - distance) / 100

            feature = np.array([ball_x, ball_y, platform_x])
            # self.q_learning_model.augment(feature, command, reward,5)            
            self.q_learning_model.update(feature, command, reward)
            

        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
        self.q_learning_model.save_table("Q_learning_model.npy")

