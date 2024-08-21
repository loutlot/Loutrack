import cv2
import numpy as np
import socket
import time
import json
import uuid
import datetime
import ntplib
from picamera2 import Picamera2

# ホストPCのIPアドレスとポート番号
HOST = 'ホストPCのIPアドレス'
PORT = 5005

# デバイスIDの生成・保存
try:
    with open('device_id.json', 'r') as f:
        device_id = json.load(f)['device_id']
except FileNotFoundError:
    device_id = str(uuid.uuid4())
    with open('device_id.json', 'w') as f:
        json.dump({'device_id': device_id}, f)

# NTPサーバーからの時刻同期
ntp_client = ntplib.NTPClient()
ntp_server = 'ntp.jst.mfeed.ad.jp'  # 日本標準時のNTPサーバー

# ソケットのセットアップ (UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Picamera2のセットアップ
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (960, 720)})
picam2.configure(camera_config)
picam2.start()

# カメラが安定するまで待機
time.sleep(2)

# 明るいエリアの矩形中心を検出する関数
def find_bright_areas(frame, threshold=200):
    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 閾値処理で明るい部分を検出
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    # 輪郭を検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 輪郭の中心を計算
    centers = []
    for contour in contours:
        if cv2.contourArea(contour) > 50:  # ノイズを避けるために小さなエリアを無視
            x, y, w, h = cv2.boundingRect(contour)
            center_x, center_y = x + w // 2, y + h // 2
            centers.append((center_x, center_y))

    return centers

# ホストからの撮影指示を待機
while True:
    sync_signal, addr = sock.recvfrom(1024)
    if sync_signal.decode('utf-8') == 'capture':
        # NTP時間の取得
        ntp_time = datetime.datetime.utcfromtimestamp(ntp_client.request(ntp_server).tx_time)
        
        # フレームを取得
        frame = picam2.capture_array()

        # 明るいエリアの矩形中心を取得
        bright_centers = find_bright_areas(frame, threshold=200)
        
        # データパケットを作成
        data = {
            'device_id': device_id,
            'ntp_time': ntp_time.isoformat(),
            'coordinates': bright_centers
        }
        
        # データをJSON形式に変換して送信
        message = json.dumps(data)
        sock.sendto(message.encode('utf-8'), (HOST, PORT))