from PIL import Image, ImageTk
from tkinter import Tk, Button, Canvas
import cv2

import detect
import scanner

# 웹캠 화면 크기 설정
FRAME_WIDTH = 800
FRAME_HEIGHT = 480

# 원근 변환 후 결과 이미지의 크기
OUTPUT_WIDTH = 680
OUTPUT_HEIGHT = 480


# Tkinter 윈도우 설정
window = Tk()
window.title("Super Easy OMR")

# 캔버스 생성
canvas = Canvas(window, width=900, height=580)
canvas.pack()

# 캔버스에 텍스트 추가
canvas.create_text(200, 50, text="Hello, Canvas!", font=("Helvetica", 20))

# 버튼을 위한 콜백 함수
def button_callback():
    print("Button clicked!")

# 버튼 생성
button = Button(window, text="Click Me", command=button_callback)

# 캔버스에 버튼 추가
canvas.create_window(200, 100, window=button)

# 웹캠 연결
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)


# 웹캠이 정상적으로 연결되었는지 확인
if not cap.isOpened():
    print('Cannot Find WebCam')
    exit()

preprocessedImg = None
# 웹캠 프레임 업데이트 함수
def update_frame():
    global preprocessedImg, canvas_image
    ret, frame = cap.read()
    if ret:
        flipped_frame = cv2.flip(frame, 1)  # 좌우 반전(거울 모드)

        # 스캔 함수에 전달하기 전에 프레임 복사본 생성
        frame_copy = flipped_frame.copy()
        captured_binary_image = scanner.scan_image(frame_copy, FRAME_WIDTH, FRAME_HEIGHT, OUTPUT_WIDTH, OUTPUT_HEIGHT)
        if captured_binary_image is not None:
            print('[INFO] Captured!')
            preprocessedImg = captured_binary_image
            return

        # Tkinter에서 보여줄 프레임 업데이트
        flipped_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
        flipped_frame = Image.fromarray(flipped_frame)
        flipped_frame = ImageTk.PhotoImage(flipped_frame)

        if canvas_image is None:
            canvas_image = canvas.create_image(200, 150, image=flipped_frame)
        else:
            canvas.itemconfig(canvas_image, image=flipped_frame)

        canvas.image = flipped_frame

    window.after(10, update_frame)


# 프레임 업데이트 시작
canvas_image = None  # 캔버스 이미지 객체 초기화
update_frame()

# Tkinter 메인 루프 실행
window.mainloop()

# 종료 시 웹캠 해제
cap.release()




detectedValues = detect.getDetectedValues(preprocessedImg)

print(detectedValues)
