from PIL import Image, ImageTk
from tkinter import Tk, Button, Canvas, Label
import cv2

import detect
import scanner

# 웹캠 화면 크기 및 출력 이미지 크기 설정
FRAME_WIDTH = 800
FRAME_HEIGHT = 480
OUTPUT_WIDTH = 680
OUTPUT_HEIGHT = 480
CANVAS_WIDTH = OUTPUT_WIDTH * 2
CANVAS_HEIGHT = int(OUTPUT_HEIGHT * 1.5)
# Tkinter 윈도우 설정
window = Tk()
window.title("Super Easy OMR Reader")

# 캔버스 생성
canvas = Canvas(window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack()

# 검출된 값 라벨
detected_values_label = Label(window, text="", font=("Helvetica", 16))
detected_values_label.pack()

# 웹캠 연결
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

if not cap.isOpened():
    print('[ERROR] Cannot Find WebCam.')
    exit()

preprocessedImg = None
detectedValues = None  # 검출된 값 변수
detectedImage = None   # 검출된 이미지 변수
webcam_image = None
gray_canvas_image = None

# 웹캠 프레임 업데이트 함수
def update_frame():
    global preprocessedImg, detectedValues, detectedImage
    global webcam_image, gray_canvas_image
    ret, frame = cap.read()
    if ret:
        flipped_frame = cv2.flip(frame, 1)
        frame_copy = flipped_frame.copy()
        captured_binary_image = scanner.scan_image(frame_copy, FRAME_WIDTH, FRAME_HEIGHT, OUTPUT_WIDTH, OUTPUT_HEIGHT)
        
        if captured_binary_image is not None:
            print('[INFO] Captured!')
            preprocessedImg = captured_binary_image
            detectedValues, detectedImage, detectStatusCode = detect.getDetectedValues(preprocessedImg)
            if detectStatusCode != 0:
                pass
            else:
                update_detected_values_label()  # 라벨 업데이트 함수 호출

        # 웹캠 화면 이미지 생성
        flipped_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
        flipped_frame = Image.fromarray(flipped_frame)
        flipped_frame = ImageTk.PhotoImage(flipped_frame.resize((FRAME_WIDTH, FRAME_HEIGHT)))

        

        # 웹캠 화면 이미지 업데이트
        if webcam_image is None:
            ### 웹캠 이미지
            webcam_image = canvas.create_image(OUTPUT_WIDTH//2, OUTPUT_HEIGHT//2, image=flipped_frame)
        else:
            canvas.itemconfig(webcam_image, image=flipped_frame)

        # 감지 화면 이미지 생성
        if detectedImage is not None:
            # detectedImage를 사용하기 위한 처리
            detected_image = cv2.cvtColor(detectedImage, cv2.COLOR_BGR2RGB)
            detected_image = Image.fromarray(detected_image)
            detected_image = ImageTk.PhotoImage(detected_image.resize((OUTPUT_WIDTH, OUTPUT_HEIGHT)))  # 크기 조정
        else:
            # 회색 화면 이미지 생성
            detected_image = Image.new('RGB', (OUTPUT_WIDTH, OUTPUT_HEIGHT), color='gray')
            detected_image = ImageTk.PhotoImage(detected_image)

        # 감지 화면 이미지 업데이트
        if gray_canvas_image is None:
            gray_canvas_image = canvas.create_image(OUTPUT_WIDTH + OUTPUT_WIDTH//2, OUTPUT_HEIGHT//2, image=detected_image)
        else:
            canvas.itemconfig(gray_canvas_image, image=detected_image)

        canvas.image = flipped_frame
        canvas.gray_image = detected_image

    window.after(10, update_frame)

# 검출된 값을 표시하는 라벨 업데이트 함수
def update_detected_values_label():
    if detectedValues is not None:
        detected_values_label.config(text=str(detectedValues))


update_frame()

window.mainloop()

cap.release()