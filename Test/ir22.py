from picamera2 import Picamera2
import cv2
import numpy as np

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

def draw_cross_and_coords(frame, points):
    for point in points:
        x, y = point

        # 十字を描画
        cv2.drawMarker(frame, (x, y), color=(0, 255, 0), markerType=cv2.MARKER_CROSS, thickness=2)

        # 座標数値を描画
        cv2.putText(frame, f"({x}, {y})", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

def main():
    # Picamera2のセットアップ
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (1280, 720)})
    picam2.configure(camera_config)
    picam2.start()

    while True:
        # フレームを取得
        frame = picam2.capture_array()

        # 明るいエリアの矩形中心を取得
        bright_centers = find_bright_areas(frame, threshold=200)

        # 十字と座標を描画
        draw_cross_and_coords(frame, bright_centers)

        # ウィンドウに表示
        cv2.imshow("Bright Areas Tracking", frame)

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # リソースを解放
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()