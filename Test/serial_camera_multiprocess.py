import cv2
import numpy as np
import socket
import time
import json
import uuid
import datetime
import ntplib
from picamera2 import Picamera2
from multiprocessing import Process, Queue

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

def capture_frames(queue):
    """カメラからフレームを取得してキューに送信するプロセス"""
    while True:
        frame = picam2.capture_array()
        queue.put(frame)

def process_frames(queue, result_queue):
    """フレームの処理を行い、結果をキューに送信するプロセス"""
    def find_bright_areas(frame, threshold=200):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        centers = []
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w // 2, y + h // 2
                centers.append((center_x, center_y))
        return centers

    while True:
        frame = queue.get()
        bright_centers = find_bright_areas(frame)
        result_queue.put(bright_centers)

def send_data(result_queue):
    """処理結果をホストPCに送信するプロセス"""
    while True:
        bright_centers = result_queue.get()
        ntp_time = datetime.datetime.utcfromtimestamp(ntp_client.request(ntp_server).tx_time)
        data = {
            'device_id': device_id,
            'ntp_time': ntp_time.isoformat(),
            'coordinates': bright_centers
        }
        message = json.dumps(data)
        sock.sendto(message.encode('utf-8'), (HOST, PORT))

if __name__ == "__main__":
    frame_queue = Queue(maxsize=10)
    result_queue = Queue(maxsize=10)

    capture_process = Process(target=capture_frames, args=(frame_queue,))
    process_process = Process(target=process_frames, args=(frame_queue, result_queue))
    send_process = Process(target=send_data, args=(result_queue,))

    capture_process.start()
    process_process.start()
    send_process.start()

    capture_process.join()
    process_process.join()
    send_process.join()