# Real-Time 3D Tracking System

**English:**  
This project is a work-in-progress real-time 3D tracking system designed to operate with multiple Raspberry Pi cameras. The system is capable of capturing and tracking 3D coordinates using a network of Raspberry Pi 5 devices with Picamera2, which communicate with a central host PC.

**日本語:**  
このプロジェクトは、複数のRaspberry Piカメラを使用してリアルタイムで3Dトラッキングを行うシステムです。Raspberry Pi 5デバイスとPicamera2を使用し、中央ホストPCと通信しながら3D座標をキャプチャおよびトラッキングすることができます。現在、制作中です。

## Project Structure / プロジェクト構成

**English:**  
The project consists of scripts for both the host PC and the Raspberry Pi camera devices. Each script is responsible for a specific part of the system, as described below:

**日本語:**  
このプロジェクトは、ホストPCとRaspberry Piカメラデバイスのためのスクリプトで構成されています。各スクリプトは、以下に説明するように、システムの特定の部分を担当します。

### Host PC Scripts / ホストPCのスクリプト

- **`send_settings.py`**  
  **English:** Sends configuration settings to all Raspberry Pi devices via broadcast.  
  **日本語:** 設定情報をブロードキャストで全Raspberry Piデバイスに送信します。

- **`calibration_host.py`**  
  **English:** Triggers the Raspberry Pi cameras to capture images for calibration, and processes the data to calibrate the system.  
  **日本語:** キャリブレーションのためにRaspberry Piカメラに画像キャプチャをトリガーし、システムのキャリブレーションを行います。

- **`live_tracking_host.py`**  
  **English:** Performs real-time 3D tracking based on the calibrated data and incoming data from the Raspberry Pi cameras.  
  **日本語:** キャリブレーションデータとRaspberry Piカメラからのデータに基づいて、リアルタイムの3Dトラッキングを行います。

### Raspberry Pi Camera Scripts / Raspberry Piカメラスクリプト

- **`receive_settings.py`**  
  **English:** Receives configuration settings from the host and manages the start/stop of the capture process.  
  **日本語:** ホストから設定情報を受信し、キャプチャプロセスの開始/停止を管理します。

- **`capture_script.py`**  
  **English:** Captures images based on the received settings and sends the processed data back to the host for tracking.  
  **日本語:** 受信した設定に基づいて画像をキャプチャし、処理されたデータをホストに送信してトラッキングを行います。

## Work in Progress / 制作中

**English:**  
Please note that this project is still under development. Some features may be incomplete or subject to change. Contributions and feedback are welcome.

**日本語:**  
このプロジェクトは現在開発中であることにご注意ください。一部の機能は未完成であるか、変更される可能性があります。貢献やフィードバックを歓迎します。
