import socket
import json
import os
import threading
import subprocess

# ソケットのセットアップ (UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 5006))  # すべてのインターフェースで受信

print("Waiting for settings from host...")

def apply_settings(settings):
    # 受信した設定情報をファイルに保存
    with open('camera_settings.json', 'w') as f:
        json.dump(settings, f)
    
    # カメラの再設定やキャプチャスクリプトの再起動を行う
    print("Applying new settings...")
    if 'restart' in settings and settings['restart']:
        subprocess.Popen(['python3', 'capture_script.py'])

# 設定受信スクリプトはバックグラウンドで動作
def listen_for_settings():
    while True:
        data, addr = sock.recvfrom(1024)
        settings = json.loads(data.decode('utf-8'))
        apply_settings(settings)
        if 'stop_capture' in settings and settings['stop_capture']:
            print("Stopping capture script...")
            os.system('pkill -f capture_script.py')

# 設定受信スレッドを開始
settings_thread = threading.Thread(target=listen_for_settings)
settings_thread.daemon = True  # メインスクリプト終了時に終了する
settings_thread.start()

# 最初の設定受信を待機
data, addr = sock.recvfrom(1024)
initial_settings = json.loads(data.decode('utf-8'))
apply_settings(initial_settings)

# キャプチャスクリプトの起動
subprocess.Popen(['python3', 'capture_script.py'])

# メインスレッドは設定受信スレッドが動作し続ける
settings_thread.join()
