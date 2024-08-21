import numpy as np
import cv2
import socket
import json
from sklearn.linear_model import RANSACRegressor
from pykalman import KalmanFilter

# キャリブレーションデータを読み込み
with open('calibration_data.json', 'r') as f:
    calibration_data = json.load(f)

# ソケットのセットアップ (UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5005))

def triangulate_point(point_A, point_B, proj_matrix_A, proj_matrix_B):
    point_4D = cv2.triangulatePoints(proj_matrix_A, proj_matrix_B, point_A.T, point_B.T)
    point_3D = cv2.convertPointsFromHomogeneous(point_4D.T)
    return point_3D

# トラッキングループ
kalman_filter = KalmanFilter(initial_state_mean=np.zeros(3), n_dim_obs=3)
previous_state = np.zeros(3)

while True:
    data_A, addr_A = sock.recvfrom(1024)
    data_B, addr_B = sock.recvfrom(1024)
    
    message_A = json.loads(data_A.decode('utf-8'))
    message_B = json.loads(data_B.decode('utf-8'))
    
    # 各カメラの座標を取得
    points_A = np.array(message_A['coordinates'], dtype=np.float32).T
    points_B = np.array(message_B['coordinates'], dtype=np.float32).T
    
    # カメラの射影行列を取得
    proj_matrix_A = np.hstack((np.array(calibration_data[message_A['device_id']]['camera_matrix']),
                               np.array(calibration_data[message_A['device_id']]['tvecs'][0]).T))
    proj_matrix_B = np.hstack((np.array(calibration_data[message_B['device_id']]['camera_matrix']),
                               np.array(calibration_data[message_B['device_id']]['tvecs'][0]).T))
    
    # 三角測量による3D位置の計算
    points_3D = triangulate_point(points_A, points_B, proj_matrix_A, proj_matrix_B)
    
    # RANSACによるエラーデータ除去
    ransac = RANSACRegressor()
    ransac.fit(points_3D, np.ones(len(points_3D)))
    inlier_mask = ransac.inlier_mask_
    filtered_points_3D = points_3D[inlier_mask]
    
    # カルマンフィルタによる平滑化と予測
    filtered_points_3D = np.reshape(filtered_points_3D, (-1, 3))
    smoothed_state, _ = kalman_filter.smooth(filtered_points_3D)
    
    print("Smoothed 3D Coordinates:", smoothed_state[-1])