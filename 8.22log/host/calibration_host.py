import numpy as np
import cv2
import socket
import json
import time

# カメラのキャリブレーションに使用するL字型ターゲットの3D座標（例：メートル単位）
object_points = np.array([
    [0, 0, 0],
    [0.210, 0, 0],
    [0, 0.297, 0]
], dtype=np.float32)

# カメラごとの2D座標を保存する辞書
image_points = {}

# ソケットのセットアップ (UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 5005))

# カメラデバイスにキャリブレーション用のトリガーを送信
for i in range(10):  # 10回キャリブレーション用データを収集
    trigger_message = 'capture'
    sock.sendto(trigger_message.encode('utf-8'), ('<broadcast>', 5006))
    
    time.sleep(0.5)  # 画像キャプチャの間に少し待機
    
    data, addr = sock.recvfrom(1024)
    message = json.loads(data.decode('utf-8'))
    device_id = message['device_id']
    coordinates = np.array(message['coordinates'], dtype=np.float32)
    
    if device_id not in image_points:
        image_points[device_id] = []
    
    image_points[device_id].append(coordinates)

# カメラごとのキャリブレーション
calibration_data = {}
for device_id, points in image_points.items():
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera([object_points] * len(points), points, (1280, 720), None, None)
    
    # 外れ値の除去（必要に応じて）
    ransac = RANSACRegressor()
    ransac.fit(points, np.ones(len(points)))
    inlier_mask = ransac.inlier_mask_
    
    calibration_data[device_id] = {
        'camera_matrix': mtx.tolist(),
        'dist_coeffs': dist.tolist(),
        'rvecs': [rvec.tolist() for rvec in rvecs],
        'tvecs': [tvec.tolist() for tvec in tvecs],
        'inliers': inlier_mask.tolist()
    }

# キャリブレーション結果を保存
with open('calibration_data.json', 'w') as f:
    json.dump(calibration_data, f, indent=4)

print("Calibration complete and saved to calibration_data.json")