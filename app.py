from PIL import Image, ImageTk
from tkinter import Tk, Button, Canvas, Label, messagebox, Menu, Toplevel, PhotoImage
import cv2
import datetime

import detector
import scanner
from properties import status, values
import answer_parser
import answer_evaluator


evaluated_values_label = None
evaluated_point_label = None
log_label = None

detected_img = None
webcam_img = None
gray_canvas_img = None

detected_id = None
detected_answer = None
total_sum_score = None


prev_detected_id = None
save_count = 0


def addDataToFile(file_path, data):
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(data + '\n')
    except FileNotFoundError:
        doLog(canvas, f'[ERROR] Cannot Find {file_path}.', values.LOG_ERR)
    except IOError:
        doLog(canvas, f'[ERROR] Cannot Write {file_path}.', values.LOG_ERR)
    except Exception as e:
        doLog(canvas, f'[ERROR] {e}.', values.LOG_ERR)


def doSave(e=None):
    global detected_id, detected_answer, total_sum_score, prev_detected_id, save_count
    if detected_id is None or detected_answer is None or total_sum_score is None:
        doLog(canvas, '[ERROR] Cannot Save. No Detected Sheet.', values.LOG_ERR)
        return
    elif prev_detected_id == detected_id:
        doLog(canvas, '[ERROR] Cannot Save. Already Saved (Id duplicates).', values.LOG_ERR)
        return
    else:
        save_count += 1
        doLog(canvas, f'[INFO] Saved {detected_id}\'s data. Count : {save_count}', values.LOG_INFO)
        addDataToFile(file_name, f'{detected_id}, {detected_answer}, {total_sum_score}')
        prev_detected_id = detected_id
        return
    

def update_evaluated_values_label(canvas, text, x, y):
    global evaluated_values_label
    if evaluated_values_label is not None:
        canvas.delete(evaluated_values_label)
    evaluated_values_label = canvas.create_text(x, y, text=text, font=("Courier", 18), justify='left', fill='#88FFAA')


def update_evaluated_point_label(canvas, text, x, y):
    global evaluated_point_label
    if evaluated_point_label is not None:
        canvas.delete(evaluated_point_label)
    evaluated_point_label = canvas.create_text(x, y, text=text, font=("Helvetica", 54), justify='left', fill='#FF0000')


def doLog(canvas, text, color='#FFFFFF'):
    global log_label
    if log_label is not None:
        canvas.delete(log_label)
    print(text)
    log_label = canvas.create_text(values.OUTPUT_WIDTH, values.OUTPUT_HEIGHT + 220, text=text, font=("Helvetica", 18), justify='left', fill=color)

# 도움말
def show_help():
    messagebox.showinfo(
        "Help",
        '''
            1. Hold the answer sheet close enough to fit the 'Live WebCam Scanner' screen. The border of the answer sheet must be clearly visible.
            2. The answers on the answer sheet are automatically detected. After checking the information, press the Save button or space bar to save.
            3. After saving all answers, exit the program. Answer data will be saved as a txt file.
        '''
    )

# 이 프로그램에 대하여..
def show_about():
    messagebox.showinfo(
        "About",
        '''
            SUPER EASY OMR READER
            This program is made by KyeongTae Ko.
            If you have any questions, please contact me at kraftenty@gmail.com.
        '''
    )


def show_splash_screen(root):
    splash = Toplevel(root)
    splash.overrideredirect(True)
    splash.geometry("600x400")

    splash_image = PhotoImage(file="image/splash.png")

    # 스플래시 화면 크기 및 위치 설정
    splash_width = splash_image.width()
    splash_height = splash_image.height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width/2) - (splash_width/2))
    y_coordinate = int((screen_height/2) - (splash_height/2))
    splash.geometry(f"{splash_width}x{splash_height}+{x_coordinate}+{y_coordinate}")

    label = Label(splash, image=splash_image)
    label.image = splash_image
    label.pack()

    splash.after(3000, splash.destroy)


# 웹캠 프레임 업데이트 함수
def update_frame():
    global detected_img
    global webcam_img, gray_canvas_img
    global evaluated_values_label, evaluated_point_label
    global detected_id, detected_answer, total_sum_score
    ret, frame = cap.read()
    if ret:
        flipped_frame = cv2.flip(frame, 1)
        scanned_binary_img = scanner.scan_image(flipped_frame, values.FRAME_WIDTH, values.FRAME_HEIGHT, values.OUTPUT_WIDTH, values.OUTPUT_HEIGHT)
        if scanned_binary_img is not None:
            detected_values, detected_img, getDetectedValues_status_code = detector.getDetectedValues(scanned_binary_img)
            if getDetectedValues_status_code == status.SUCCESSFUL['code']:
                doLog(canvas, '[INFO] Captured!', values.LOG_INFO)
                # 채점 부분
                detected_id = detected_values[0]
                detected_answer = detected_values[2] + detected_values[3]
                total_sum_score, OX_map, score_map = answer_evaluator.evaluateAnswer(detected_answer, answer_map)
                student_id = detected_values[0]
                is_safecode_valid = 'Valid' if detected_values[1] else 'Invalid'
                safecode = detected_values[4]
                correct_answer_li = [answer_map[i]['answer'] for i in answer_map.keys()]
                doLog(canvas, f'[INFO] Correct answer : {correct_answer_li}', values.LOG_INFO)
                doLog(canvas, f'[INFO] Answer detected : {detected_answer}', values.LOG_INFO)
                
                problem_number_text = ' '.join([str(i) if i>=10 else '0'+str(i) for i in score_map.keys()])
                problem_score_text = ' ' + '  '.join([str(i) for i in score_map.values()])
                ox_text = ' ' + '  '.join([str(i) for i in OX_map.values()])
                update_evaluated_values_label(
                    canvas,
                    f'''
                        Student ID        : {student_id}
                        Safecode          : {safecode}
                        Is SafeCode Valid : {is_safecode_valid}
                        Total Score       : {total_sum_score}
                        --------------------------------------------------------------------------------
                        Problem Num.      : {problem_number_text}
                        OX                : {ox_text}
                        Point             : {problem_score_text}
                    ''',
                    values.OUTPUT_WIDTH//2, 
                    values.OUTPUT_HEIGHT+120, 
                )
                update_evaluated_point_label(
                    canvas,
                    f'{total_sum_score}',
                    values.OUTPUT_WIDTH*2 - 100, 
                    values.OUTPUT_HEIGHT + 100, 
                )


        # 웹캠 이미지 부분
        color_modified_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
        photofied_frame = ImageTk.PhotoImage(Image.fromarray(color_modified_frame).resize((values.FRAME_WIDTH, values.FRAME_HEIGHT)))
        # 웹캠 이미지 업데이트    
        if webcam_img is None: # 웹캠 이미지가 없으면 할당
            webcam_img = canvas.create_image(values.OUTPUT_WIDTH//2, values.OUTPUT_HEIGHT//2, image=photofied_frame)
        else: # 있으면 이미지 넣어서 업데이트
            canvas.itemconfig(webcam_img, image=photofied_frame)

        # 감지 화면 이미지 부분
        if detected_img is None: # 감지된 것이 없으면 회색 이미지 생성
            photofied_detected_img = ImageTk.PhotoImage(Image.new('RGB', (values.OUTPUT_WIDTH, values.OUTPUT_HEIGHT), color='gray'))
        else:                    # 감지된 것이 있으면 점마킹처리된 이미지 사용
            color_modified_detected_img = cv2.cvtColor(detected_img, cv2.COLOR_BGR2RGB)
            photofied_detected_img = ImageTk.PhotoImage(Image.fromarray(color_modified_detected_img).resize((values.OUTPUT_WIDTH, values.OUTPUT_HEIGHT)))
        # 감지 화면 이미지 업데이트
        if gray_canvas_img is None:
            gray_canvas_img = canvas.create_image(values.OUTPUT_WIDTH + values.OUTPUT_WIDTH//2, values.OUTPUT_HEIGHT//2, image=photofied_detected_img)
        else:
            canvas.itemconfig(gray_canvas_img, image=photofied_detected_img)
        
        # 캔버스에 웹캠화면과 감지화면 그려넣기
        canvas.left_img = photofied_frame
        canvas.right_img = photofied_detected_img

    root.after(200, update_frame) # 200ms마다 업데이트







# Tkinter 윈도우(root) 설정
root = Tk()

# Splash Screen 표현을 위해 root 잠시 withdraw
root.withdraw()
show_splash_screen(root)
root.after(3000, root.deiconify)

# Splash Screen 표시 중에 시간 좀 걸리는것들 처리
# answer map 가져오기
answer_map = answer_parser.getAnswerMap()
print(f'[INFO] {len(answer_map)} Answers Loaded.')

# 웹캠 연결
cap = cv2.VideoCapture(0)
cap.set(3, values.FRAME_WIDTH)
cap.set(4, values.FRAME_HEIGHT)

# root 재개
root.title("Super Easy OMR Reader")
root.resizable(False, False)



# 메뉴바 생성
menubar = Menu(root)
info_menu = Menu(menubar, tearoff=0)
info_menu.add_command(label="Help", command=show_help)
info_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Info", menu=info_menu)
control_menu = Menu(menubar, tearoff=0)
control_menu.add_command(label="Bye", command=exit)
menubar.add_cascade(label="End", menu=control_menu)
root.config(menu=menubar)


# 캔버스 생성
canvas = Canvas(root, width=values.CANVAS_WIDTH, height=values.CANVAS_HEIGHT, bg='#222222')
canvas.pack()

# 설명 달기
canvas.create_text(values.OUTPUT_WIDTH//2, values.OUTPUT_HEIGHT+10, text='Live WebCam Scanner', font=("Helvetica", 20))
canvas.create_text(values.OUTPUT_WIDTH + values.OUTPUT_WIDTH//2, values.OUTPUT_HEIGHT+10, text='Detected Sheet', font=("Helvetica", 20))

# 버튼 달기
save_button = Button(root, text='Save', command = lambda: doSave(), width=10, height=2)
save_button.pack()

# 스페이스바 설명 라벨 달기
Label(root, text='You can also save by pressing the SpaceBar', font=("Helvetica", 14)).pack()

# 스페이스바 처리부분
root.bind('<space>', doSave)
root.focus_set()


# 웹캠 연결 확인
if not cap.isOpened():
    doLog(canvas, '[ERROR] Cannot Find WebCam.', values.LOG_ERR)
    exit()
else:
    doLog(canvas, '[INFO] WebCam Connected.', values.LOG_INFO)
    

# 파일 처리
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
file_name = f'{current_time}.txt'
doLog(canvas, f'[INFO] Load Success. Answer File will be saved as {file_name}', values.LOG_INFO)


# 루프 돌아가는 부분
update_frame()
root.mainloop()
cap.release()