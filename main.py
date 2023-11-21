import preprocess
import cv2
import numpy as np

WIDTH = 680
HEIGHT = 480

preprocessedImg = preprocess.getProcessedImage()
cv2.imshow("preprocessedImg", preprocessedImg)

# 이미지 이진화 (imtres = 이진화된 이미지)
_, imthres = cv2.threshold(preprocessedImg, 220, 255, cv2.THRESH_BINARY_INV)
# 점 찾기
contours, _ = cv2.findContours(imthres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# 컬러로 변환한 이미지 (점찍기위해서)
color_img = cv2.cvtColor(preprocessedImg, cv2.COLOR_GRAY2BGR)


### Guide 찾기 ----------------------------------------------
upper_guides = []
right_guides = []

for contour in contours:
    # 각 컨투어의 경계 상자 좌표 구하기
    x, y, w, h = cv2.boundingRect(contour)
    # 중심점 좌표 계산
    cx = x + w // 2
    cy = y + h // 2
    # 중심점이 위에서 15px 이내이면 upper_guides에 추가
    if cy <= 15: 
        cv2.circle(color_img, (cx, cy), 5, (255, 0, 0), -1)
        upper_guides.append((cx, cy))
    # 중심점이 오른쪽에서 15px 이내이면 right_guides에 추가
    if cx >= WIDTH - 15:
        cv2.circle(color_img, (cx, cy), 5, (255, 0, 0), -1)
        right_guides.append((cx, cy))

upper_guides.sort(key=lambda x: x[0]) # 왼쪽에 있는(x값이 작은) 점부터 정렬
right_guides.sort(key=lambda x: x[1]) # 위에 있는(y값이 작은) 점부터 정렬

# 디버그용
print(f'upper_guides={upper_guides}')
print(f'right_guides={right_guides}')


### 점 찍기 --------------------------------------------------
MATRIX_WIDTH = len(upper_guides) # 19
MATRIX_HEIGHT = len(right_guides) # 12
if MATRIX_WIDTH != 19 and MATRIX_HEIGHT != 12:
    print('[ERROR] The number of recognized guide points is incorrect.')
    print('        ERROR CODE 5')
    exit(5)

ptr_matrix = [[0 for _ in range(MATRIX_WIDTH)] for _ in range(MATRIX_HEIGHT)]
 
# 점 검사 핵심 루프
for rightIdx, rightPtr in enumerate(right_guides):
    for upIdx, upperPtr in enumerate(upper_guides):
        # 점이 찍혀있는지 확인하고 싶음
        # 바이너리 이미지의 해당 좌표에 마킹이 없다면
        if imthres[rightPtr[1], upperPtr[0]] == 0:
            # 해당 좌표에 마킹이 없으면 빨간점
            cv2.circle(color_img, (upperPtr[0], rightPtr[1]), 3, (0, 0, 255), -1)
            ptr_matrix[rightIdx][upIdx] = 0

        else:
            # 해당 좌표에 마킹이 있으면 초록점
            cv2.circle(color_img, (upperPtr[0], rightPtr[1]), 3, (0, 255, 0), -1)
            ptr_matrix[rightIdx][upIdx] = 1

# DEBUG
for y in range(MATRIX_HEIGHT):
    for x in range(MATRIX_WIDTH):
        print(ptr_matrix[y][x], end='')
    print()

# DEBUG     111111111
# 0123456789012345678            
# 1000000000100010001 0
# 0100000000100010000 1
# 0010000000100010001 2
# 0001000000100010000 3
# 0000100000100010000 4
# 0000010000100010001 5
# 0000001000100010000 6
# 0000000100100010001 7
# 0000000000100010000 8
# 0000000000100010000 9
# 0000000000100010000 10
# 0000000000100010000 11


## 학번(ID) 검출---------------------------------------------
id = ''
for x in range(8):
    for y in range(10):
        was_read_in_col = False
        if ptr_matrix[y][x] == 1:
            if not was_read_in_col:
                id += str(y)
                was_read_in_col = True
            else:
                print('[ERROR] ID marking is duplicated. ID is not readable.')
                print('        ERROR CODE 6')
                exit(6)

            
print(f'id={id}')
########
# SAFECODE
# 0,7 / 0,7  : 1
# 0,7 / 4,11 : 2
# 4,11 / 0,7 : 3
# 4,11 / 4,11: 4
########
## 세이프코드 검출 0,4,7,11-----------------------------------------
SAFECODE_LINE = 18
first_answerline_safenums = []
second_answerline_safenums = []

def getSafeCode(first_answerline_safenums_arg, second_answerline_safenums_arg):
    if first_answerline_safenums_arg == [0,7] and second_answerline_safenums_arg == [0,7]:
        return 1
    elif first_answerline_safenums_arg == [0,7] and second_answerline_safenums_arg == [4,11]:
        return 2
    elif first_answerline_safenums_arg == [4,11] and second_answerline_safenums_arg == [0,7]:
        return 3
    elif first_answerline_safenums_arg == [4,11] and second_answerline_safenums_arg == [4,11]:
        return 4
    else:
        return -1

for y, code_idx in enumerate((0,4,7,11,0,4,7,11)):
    if ptr_matrix[y][SAFECODE_LINE] == 1:
        if y < 4:
            first_answerline_safenums.append(code_idx)
        else:
            second_answerline_safenums.append(code_idx)

if len(first_answerline_safenums) != 2 or len(second_answerline_safenums) != 2:
    print('[ERROR] The number of safecode is incorrect.')
    print('        ERROR CODE 7')
    exit(7)

safeCode = getSafeCode(first_answerline_safenums, second_answerline_safenums)
print(f'safeCode={safeCode}')

print(f'first_answerline_safenums={first_answerline_safenums}')
print(f'second_answerline_safenums={second_answerline_safenums}')

## 첫번째 정답라인 정답 검출-----------------------------------------
first_answerline_answers = []
for y in range(0, 12):
    if y in first_answerline_safenums: # safecode 문항이면
        if ptr_matrix[y][8 + safeCode - 1] != 1:
            print('[ERROR] First answerline safecode is incorrect.')
    else: # 일반문항이면
        for x in range(8, 13): # 8~12번째 컬럼
            was_read_in_row = False
            if ptr_matrix[y][x] == 1:
                if not was_read_in_row:
                    first_answerline_answers.append(x-7)
                    was_read_in_row = True
                else:
                    print('[ERROR] First answerline answer marking is duplicated. Answer is not readable.')
                    print('        ERROR CODE 8')
                    exit(8)

print(f'first_answerline_answers={first_answerline_answers}')

## 두번째 정답라인 정답 검출-----------------------------------------
second_answerline_answers = []
for y in range(0, 12):
    if y in second_answerline_safenums: # safecode 문항이면
        if ptr_matrix[y][13 + safeCode - 1] != 1:
            print('[ERROR] Second answerline safecode is incorrect.')
    else: # 일반문항이면
        for x in range(13, 18): # 13~17번째 컬럼
            was_read_in_row = False
            if ptr_matrix[y][x] == 1:
                if not was_read_in_row:
                    second_answerline_answers.append(x-12)
                    was_read_in_row = True
                else:
                    print('[ERROR] Second answerline answer marking is duplicated. Answer is not readable.')
                    print('        ERROR CODE 9')
                    exit(9)

print(f'second_answerline_answers={second_answerline_answers}')






# 점 찍힌 이미지
cv2.imshow("Result", color_img)
cv2.waitKey(0)
cv2.destroyAllWindows()


# 이진처리된 이미지
cv2.imshow("Result", preprocessedImg)
cv2.waitKey(0)
cv2.destroyAllWindows()