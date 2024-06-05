import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage import gaussian_filter
import pandas as pd
import pickle

def read_ball_info(file_path):
    trajectories = []
    with open(file_path, 'r') as file:
        current_trajectory = []
        for line in file:
            line = line.strip()
            if line:
                x, y = map(float, line.split(','))
                current_trajectory.append((x, y))
            else:
                if current_trajectory:
                    trajectories.append(current_trajectory)
                    current_trajectory = []
        if current_trajectory:
            trajectories.append(current_trajectory)
    return trajectories


def generate_heatmap(trajectories, grid_size=(200, 500)):
    x_coords = []
    y_coords = []
    for trajectory in trajectories:
        for x, y in trajectory:
            x_coords.append(x)
            y_coords.append(y)
    
    heatmap, _, _ = np.histogram2d(x_coords, y_coords, bins=grid_size)
    return heatmap.T


def plot_heatmap(frequency_matrix):

    frequency_matrix_smoothed = gaussian_filter(frequency_matrix, sigma=1)

    plt.figure(figsize=(4, 10),tight_layout=True)
    sns.heatmap(frequency_matrix_smoothed, cmap='Blues', cbar=True, xticklabels=False, yticklabels=False)
    plt.title('Ball')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.savefig("heatmap.jpg")


def heatmap(file_path):
    trajectories = read_ball_info(file_path)
    frequency_matrix = generate_heatmap(trajectories)
    plot_heatmap(frequency_matrix)

def linechart(file_path):    
    data = pd.read_csv(file_path, header=None)
    data = data.squeeze()
    time = range(len(data))
    plt.figure(figsize=(10, 6))
    plt.plot(time, data, linestyle='-', color='b')
    plt.xlabel('Scores')
    plt.ylabel('Ball Catch Times')
    plt.title('Traning')
    plt.savefig("linechart.jpg")

def histogram(file_path):
    title_list = ['ball_x', 'ball_y', 'ball_speed_x', 'ball_speed_y']
    max_num_list = [200, 500, 40, 40]

    with open(file_path, 'rb') as file:
        data = pickle.load(file)

        plt.figure(figsize=(10, 8))

        num_columns = len(data[0])  # 假设每一行的数据长度一致

        for i in range(num_columns):
            column_data = [row[i] for row in data]  # 提取每一列的数据
            scaled_data = [value * max_num_list[i] for value in column_data]  # 根据比例缩放数据

            plt.subplot(1, len(title_list), i+1)
            plt.hist(scaled_data, bins=20, edgecolor='black')
            plt.title(f'{title_list[i]}') 
            plt.xlabel(title_list[i])  # 设置 x 轴标签
            plt.ylabel('Frequency')  # 设置 y 轴标签

        plt.tight_layout()
        plt.savefig("histogram.jpg")


if __name__ == "__main__":
    file_path = 'ball_HITPOINT.txt'
    trajectories = read_ball_info(file_path)
    frequency_matrix = generate_heatmap(trajectories)
    plot_heatmap(frequency_matrix)
