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


def plot_heatmap(frequency_matrix,visualize_data):

    frequency_matrix_smoothed = gaussian_filter(frequency_matrix, sigma=1)

    plt.figure(figsize=(4, 10),tight_layout=True)
    sns.heatmap(frequency_matrix_smoothed, cmap='Blues', cbar=True, xticklabels=False, yticklabels=False)
    plt.title(visualize_data["title"])
    plt.xlabel(visualize_data["x-axis"])
    plt.ylabel(visualize_data["y-axis"])
    plt.savefig("heatmap.jpg")


def heatmap(file_path,visualize_data):
    trajectories = read_ball_info(file_path)
    frequency_matrix = generate_heatmap(trajectories)
    plot_heatmap(frequency_matrix,visualize_data)

def linechart(file_path,visualize_data):    
    data = pd.read_csv(file_path, header=None)
    data = data.squeeze()
    time = range(len(data))
    plt.figure(figsize=(10, 6))
    plt.plot(time, data, linestyle='-', color='b')
    plt.title(visualize_data["title"])
    plt.xlabel(visualize_data["x-axis"])
    plt.ylabel(visualize_data["y-axis"])
    plt.savefig("linechart.jpg")

def histogram(file_path,visualize_data):
    title_list = []
    max_num_list = []
    for key, value in visualize_data.items():
        title_list.append(key)
        max_num_list.append(value)
    with open(file_path, 'rb') as file:
        data = pickle.load(file)        

        num_columns = len(data[0])
        plt.figure(figsize=(2*num_columns, 10))
        for i in range(num_columns):
            column_data = [row[i] for row in data]
            scaled_data = [value * max_num_list[i] for value in column_data]
            plt.subplot(1, len(title_list), i+1)
            plt.hist(scaled_data, bins=20, edgecolor='black')
            plt.title(f'{title_list[i]}') 
            plt.xlabel(title_list[i])
            plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig("histogram.jpg")


if __name__ == "__main__":
    file_path = 'ball_HITPOINT.txt'
    trajectories = read_ball_info(file_path)
    frequency_matrix = generate_heatmap(trajectories)
    plot_heatmap(frequency_matrix)
