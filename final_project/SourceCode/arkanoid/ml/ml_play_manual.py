import pygame
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
import os
import pickle
import csv
import random
# python -m mlgame -i ./ml/ml_play_manual.py . --difficulty NORMAL --level 5
class MLPlay:
    def __init__(self, *args, **kwargs):
        self.game_count = 1  # 遊戲計數器
        self.model_load()        
        self.ball_served = False
        self.record = []
        self.features = []
        self.targets = []
        self.offset = 200
        self.mapSize = int((340-self.offset)/10*40)
        print("Game" ,self.game_count, "=============================")


    def update(self, scene_info, keyboard=None):
        """
        Generate the command according to the received `scene_info`.
        """
        command = None
        if keyboard is None:
            keyboard = []
        if scene_info["status"] == "GAME_OVER":#遊戲結束
            self.game_count += 1  # 遊戲結束時遞增遊戲計數器
            return "RESET"
        elif scene_info["status"] == "GAME_PASS":#遊戲通過
            print("\nGAME_PASS!!!")
            print("第",self.game_count,"場完成")
            raise Exception("exit")
        if not self.ball_served:#發球
            command = "SERVE_TO_RIGHT"
            self.ball_served = True
        else:
            platformX = scene_info['platform'][0]
            x, y = scene_info['ball']
            frame = scene_info['frame']
            feature = self.feature_get(scene_info)
            if self.model is not None and y < 395 + 7:
                if random.random() > 0.1:#一定機率不套用模型                    
                    targetX = self.predict(feature)                    
                    if platformX + 15 > targetX:
                        command = "MOVE_LEFT"
                    elif platformX + 15 < targetX:
                        command = "MOVE_RIGHT"
                    else:
                        command = None
                else:
                    command = random.choice(["MOVE_LEFT", "MOVE_RIGHT", None])
            if y == 395:#平台接到球
                print('hit at frame ', frame)

        return command
    def reset(self):
        """
        Reset the status
        """
        DIR = os.path.dirname(__file__)

        with open(DIR + '/record' + '.csv', 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(self.record)

        self.record.reverse()

        Temp = self.feature_add(DIR, self.record)

        self.model = DecisionTreeRegressor(
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features=None)

        self.train(self.features, self.targets)

        self.model_save(DIR, Temp)

        self.ball_served = False
        self.record = []
        print("Game", self.game_count , "=============================")  # 顯示遊戲次數
    def feature_get(self, scene_info):

        frame = scene_info['frame']
        x, y = scene_info['ball']     
        dx, dy = 0, 0
        Map = [0] * self.mapSize

        for xb, yb in scene_info['bricks']:
            if yb < self.offset:
                break
            ii = int((xb / 5) + (yb - self.offset) * 4)
            if ii >= len(Map):
                print("Index out of range:", ii)
            Map[ii] = 9

        for xb, yb in scene_info['hard_bricks']:
            if yb < self.offset:
                break
            ii = int((xb / 5) + (yb - self.offset) * 4)
            Map[ii] = 10

        if frame > 0 and len(self.record) > 0:
            lastFrame, lastX, lastY, last_dx, last_dy = self.record[-1][0:5]
            dx, dy = last_dx, last_dy

            if frame - lastFrame == 1:
                dx, dy = (x - lastX) * 5, (y - lastY) * 5
        
        fv = [frame, x, y, dx, dy]
        
        fv.extend(Map)#特徵包含偵數，球xy，速度dxdy，地圖狀態
        
        self.record.append(fv)

        return fv
    
    def model_load(self):
        """
        Loads a pre-trained model from a pickle file.

        The method checks if the 'model.pickle' file exists in the same directory as the script.
        If the file exists, it loads the model from the pickle file and assigns it to the 'model' attribute of the class.
        If the file does not exist, the 'model' attribute remains None.

        Returns:
            None

        """
        self.model = None   
        DIR = os.path.dirname(__file__)
        if os.path.exists(DIR+'/model.pickle'):
            with open(DIR+'/model.pickle', 'rb') as f:
                self.model = pickle.load(f)                
            print('model loaded')

    def model_save(self, DIR, features):
        """
        Save the model, features, and targets to the specified directory.

        Args:
            DIR (str): The directory path where the files will be saved.
            features (list): The list of features to be saved.

        Returns:
            None
        """

        with open(DIR + '/features' + '.csv', 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(features)

        with open(DIR + '/features' + '.pickle', 'wb') as f:
            pickle.dump(self.features, f)
        with open(DIR + '/targets' + '.pickle', 'wb') as f:
            pickle.dump(self.targets, f)

        with open(DIR+ '/model' + '.pickle', 'wb') as f:
            pickle.dump(self.model, f)

    def feature_add(self, DIR, feature):
        """
        Adds features to the existing feature set and updates the target values.

        Args:
            DIR (str): The directory path where the feature and target files are stored.
            feature (list): A list of feature.

        Returns:
            list: A list of feature records with the target values updated.

        Raises:
            FileNotFoundError: If the feature or target files are not found in the specified directory.
        """

        if os.path.exists(DIR + '/targets.pickle'):
            with open(DIR + '/targets.pickle', 'rb') as f:
                self.targets = pickle.load(f)
            with open(DIR + '/features.pickle', 'rb') as f:
                self.features = pickle.load(f)
        ii = None
        for i in range(len(feature)):
            y = feature[i][2]
            if y >= (395 - 7) and y <= (395 + 7):
                ii = i
                break

        targetX = feature[ii][1]
        Temp = []
        i = 0
        for fv in feature[ii:]:
            frame, x, y, dx, dy = fv[0:5]
            self.features.append(fv[1:])
            self.targets.append([targetX])
            temp = [targetX]
            temp.extend(fv)
            Temp.append(temp)
            i += 1
            if y == 395 and i > 4:
                break
        print("增加feature數量:", i)

        return Temp

    def train(self, features, targets):
        """
        Trains the model using the provided features and targets.

        Parameters:
        - features (list): The input features for training the model.
        - targets (list): The target values for training the model.

        Returns:
        None
        """        
        self.model.fit(features, targets)

    def predict(self, feature):
        """
        Predicts the target X coordinate based on the given feature.

        Parameters:
        - feature (list): A list of features used for prediction.

        Returns:
        - targetX (int): The predicted target X coordinate.

        """
        targetX = int(self.model.predict([feature[1:]])[0])

        return targetX

