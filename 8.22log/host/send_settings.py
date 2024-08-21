import socket
import json

# 設定情報を定義
settings = {
    'host_ip': 'ホストPCのIPアドレス',
    'resolution': (1280, 720),
    'framerate': 30,
    'restart': True,  # キャプチャスクリプトを再起動するフラグ
    'stop_capture': False  # キャプチャスクリプトを停止するフラグ
}

# ブロードキャストアドレスとポート
BROADCAST_IP = '255.255.255.255'
PORT = 5006

# ソケットのセットアップ (UDP ブロードキャスト)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# 設定ファイルを送信
message = json.dumps(settings)
sock.sendto(message.encode('utf-8'), (BROADCAST_IP, PORT))
print("Settings broadcasted to all camera devices.")