from PIL import Image, ImageTk
from tkinter import Tk, Button, Canvas, Label
import cv2

import detect
import scanner
from properties import status, values
from answer import answer


# Tkinter 윈도우 설정
window = Tk()
window.title("Super Easy OMR Reader")

# 캔버스 생성
canvas = Canvas(window, width=values.CANVAS_WIDTH, height=values.CANVAS_HEIGHT)
canvas.pack()

# 검출된 값 라벨
detected_values_label = Label(window, text="", font=("Helvetica", 16))
detected_values_label.pack()

# 웹캠 연결
cap = cv2.VideoCapture(0)
cap.set(3, values.FRAME_WIDTH)
cap.set(4, values.FRAME_HEIGHT)

if not cap.isOpened():
    print('[ERROR] Cannot Find WebCam.')
    exit()

# preprocessed_img = None
detected_values = None  # 검출된 값 변수
detected_img = None   # 검출된 이미지 변수
webcam_image = None
gray_canvas_image = None

# 웹캠 프레임 업데이트 함수
def update_frame():
    global detected_values, detected_img
    global webcam_image, gray_canvas_image
    ret, frame = cap.read()
    if ret:
        flipped_frame = cv2.flip(frame, 1)
        scanned_binary_img = scanner.scan_image(flipped_frame, values.FRAME_WIDTH, values.FRAME_HEIGHT, values.OUTPUT_WIDTH, values.OUTPUT_HEIGHT)
        if scanned_binary_img is not None:
            print('[INFO] Captured!')
            detected_values, detected_img, getDetectedValues_status_code = detect.getDetectedValues(scanned_binary_img)
            if getDetectedValues_status_code == status.SUCCESSFUL['code']:
                detected_values_label.config(text=str(detected_values))
                # 채점 부분
                

        # 웹캠 이미지 부분
        color_modified_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
        photofied_frame = ImageTk.PhotoImage(Image.fromarray(color_modified_frame).resize((values.FRAME_WIDTH, values.FRAME_HEIGHT)))
        # 웹캠 이미지 업데이트    
        if webcam_image is None: # 웹캠 이미지가 없으면 할당
            webcam_image = canvas.create_image(values.OUTPUT_WIDTH//2, values.OUTPUT_HEIGHT//2, image=photofied_frame)
        else: # 있으면 이미지 넣어서 업데이트
            canvas.itemconfig(webcam_image, image=photofied_frame)

        # 감지 화면 이미지 부분
        if detected_img is None: # 감지된 것이 없으면 회색 이미지 생성
            photofied_detected_img = ImageTk.PhotoImage(Image.new('RGB', (values.OUTPUT_WIDTH, values.OUTPUT_HEIGHT), color='gray'))
        else:                    # 감지된 것이 있으면 점마킹처리된 이미지 사용
            color_modified_detected_img = cv2.cvtColor(detected_img, cv2.COLOR_BGR2RGB)
            photofied_detected_img = ImageTk.PhotoImage(Image.fromarray(color_modified_detected_img).resize((values.OUTPUT_WIDTH, values.OUTPUT_HEIGHT)))
        # 감지 화면 이미지 업데이트
        if gray_canvas_image is None:
            gray_canvas_image = canvas.create_image(values.OUTPUT_WIDTH + values.OUTPUT_WIDTH//2, values.OUTPUT_HEIGHT//2, image=photofied_detected_img)
        else:
            canvas.itemconfig(gray_canvas_image, image=photofied_detected_img)
        
        # 캔버스에 웹캠화면과 감지화면 그려넣기
        canvas.left_img = photofied_frame
        canvas.right_img = photofied_detected_img

    window.after(100, update_frame) # 100ms마다 업데이트




update_frame()
window.mainloop()
cap.release()