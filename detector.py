import cv2
from properties import status, values


OUTPUT_MATRIX_WIDTH = 19
OUTPUT_MATRIX_HEIGHT = 12
SAFECODE_LINE_COL_IDX = 18

UNMARK = 0
MARK = 1


def findGuides(contours, color_img):
    upper_guides = []
    right_guides = []
    for contour in contours:
        # 각 컨투어의 경계 상자 좌표 구하기
        x, y, w, h = cv2.boundingRect(contour)
        # 중심점 좌표 계산
        cx = x + w // 2
        cy = y + h // 2
        # 중심점이 위에서 15px 이내이면 upperGuidesList에 추가
        if cy <= 15:                           # B   G   R
            cv2.circle(color_img, (cx, cy), 5, (0, 255, 255), -1)
            upper_guides.append((cx, cy))
        # 중심점이 오른쪽에서 15px 이내이면 right_guides에 추가
        if cx >= values.OUTPUT_WIDTH - 15:
            cv2.circle(color_img, (cx, cy), 5, (0, 255, 255), -1)
            right_guides.append((cx, cy))

    upper_guides.sort(key=lambda x: x[0]) # 왼쪽에 있는(x값이 작은) 점부터 정렬
    right_guides.sort(key=lambda x: x[1]) # 위에 있는(y값이 작은) 점부터 정렬
    return upper_guides, right_guides


def doDot(upper_guides, right_guides, binary_img, color_img):
    if OUTPUT_MATRIX_WIDTH != len(upper_guides) and OUTPUT_MATRIX_HEIGHT != len(right_guides):
        print(status.ERR_NUM_OF_GUIDE_INCORRECT['msg'])
        return None, status.ERR_NUM_OF_GUIDE_INCORRECT['code']
    marking_tf_matrix = [[UNMARK for _ in range(OUTPUT_MATRIX_WIDTH)] for _ in range(OUTPUT_MATRIX_HEIGHT)]
    # 점 검사 핵심 루프
    for right_idx, right_ptr in enumerate(right_guides):
        for upper_idx, upper_ptr in enumerate(upper_guides):
            # 바이너리 이미지의 해당 좌표에 마킹이 없으면
            if binary_img[right_ptr[1], upper_ptr[0]] == 0:
                cv2.circle(color_img, (upper_ptr[0], right_ptr[1]), 3, (0, 0, 255), -1)
                marking_tf_matrix[right_idx][upper_idx] = UNMARK
            # 바이너리 이미지의 해당 좌표에 마킹이 있으면
            else:
                cv2.circle(color_img, (upper_ptr[0], right_ptr[1]), 3, (0, 255, 0), -1)
                marking_tf_matrix[right_idx][upper_idx] = MARK
    return marking_tf_matrix, status.SUCCESSFUL['code']


# id(학번) 검출하는 함수
def getId(marking_tf_matrix):
    id = ''
    for x in range(8):
        for y in range(10):
            was_read_in_col = False
            if marking_tf_matrix[y][x] == MARK:
                if not was_read_in_col:
                    id += str(y)
                    was_read_in_col = True
                else:
                    print(status.ERR_ID_MARKING_DUPLICATED['msg'])
                    return None, status.ERR_ID_MARKING_DUPLICATED['code']
    return id, status.SUCCESSFUL['code']


# safenum 위치 알아내서 반환하는 함수
def getSafeNums(marking_tf_matrix):
    first_answerline_safenums = []
    second_answerline_safenums = []
    for y, code_idx in enumerate((0,4,7,11,0,4,7,11)):
        if marking_tf_matrix[y][SAFECODE_LINE_COL_IDX] == MARK:
            if y < 4:
                first_answerline_safenums.append(code_idx)
            else:
                second_answerline_safenums.append(code_idx)
    if len(first_answerline_safenums) != 2 or len(second_answerline_safenums) != 2:
        print(status.ERR_NUM_OF_SAFENUM_INCORRECT['msg'])
        return None, None, status.ERR_NUM_OF_SAFENUM_INCORRECT['code']
    
    return first_answerline_safenums, second_answerline_safenums, status.SUCCESSFUL['code']


# safecode 생성하는 함수
def getSafeCode(first_answerline_safenums, second_answerline_safenums):
    ####################
    # SAFECODE         #
    # 0,7  / 0,7   : 1 #
    # 0,7  / 4,11  : 2 #
    # 4,11 / 0,7   : 3 #
    # 4,11 / 4,11  : 4 #
    ####################
    if first_answerline_safenums == [0,7] and second_answerline_safenums == [0,7]:
        return 1, status.SUCCESSFUL['code']
    elif first_answerline_safenums == [0,7] and second_answerline_safenums == [4,11]:
        return 2, status.SUCCESSFUL['code']
    elif first_answerline_safenums == [4,11] and second_answerline_safenums == [0,7]:
        return 3, status.SUCCESSFUL['code']
    elif first_answerline_safenums == [4,11] and second_answerline_safenums == [4,11]:
        return 4, status.SUCCESSFUL['code']
    else:
        print(status.ERR_NO_MATCHING_SAFECODE['msg'])
        return -1, status.ERR_NO_MATCHING_SAFECODE['code']


# 첫번째 정답라인 정답 검출하는 함수
def getFirstAnswerlineAnswers(marking_tf_matrix, first_answerline_safenums, safecode): 
    first_answerline_answers = []
    is_first_answerline_safecode_valid = True
    for y in range(0, 12):
        if y in first_answerline_safenums:   # safecode 문항이면
            if marking_tf_matrix[y][8 + safecode - 1] == UNMARK:
                print('[ERROR] First answerline safecode is incorrect.')
                is_first_answerline_safecode_valid = False
        else:                                # 일반문항이면
            multiple_answer_list = list()
            for x in range(8, 13): # 8~12번째 컬럼
                if marking_tf_matrix[y][x] == MARK:
                    multiple_answer_list.append(x-7)
            if len(multiple_answer_list) == 1:                # 단수정답이면
                first_answerline_answers.append(multiple_answer_list[0])
            else:                                             # 복수정답이면
                first_answerline_answers.append(tuple(multiple_answer_list))

    return first_answerline_answers, is_first_answerline_safecode_valid

# 두번째 정답라인 정답 검출하는 함수
def getSecondAnswerlineAnswers(marking_tf_matrix, second_answerline_safenums, safecode):
    second_answerline_answers = []
    is_second_answerline_safecode_valid = True
    for y in range(0, 12):
        if y in second_answerline_safenums:     # safecode 문항이면
            if marking_tf_matrix[y][13 + safecode - 1] == UNMARK:
                print('[ERROR] Second answerline safecode is incorrect.')
                is_second_answerline_safecode_valid = False
        else:                                   # 일반문항이면
            multiple_answer_list = list()
            for x in range(13, 18): # 13~17번째 컬럼
                if marking_tf_matrix[y][x] == MARK:
                    multiple_answer_list.append(x-12)
            if len(multiple_answer_list) == 1:                # 단수정답이면
                second_answerline_answers.append(multiple_answer_list[0])
            else:                                             # 복수정답이면
                second_answerline_answers.append(tuple(multiple_answer_list))
    return second_answerline_answers, is_second_answerline_safecode_valid


# 검출된 값들을 반환하는 함수 (main.py에서 호출)
def getDetectedValues(preprocessed_img):
    # 이미지 이진화
    _, binary_img = cv2.threshold(preprocessed_img, 220, 255, cv2.THRESH_BINARY_INV)
    # 점 찾기
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 컬러로 변환한 이미지 (점찍기위해서)
    color_img = cv2.cvtColor(preprocessed_img, cv2.COLOR_GRAY2BGR)
    # 가이드 찾기
    upper_guides, right_guides = findGuides(contours, color_img)
    # 점 찍기
    marking_tf_matrix, doDot_status_code = doDot(upper_guides, right_guides, binary_img, color_img)
    if doDot_status_code != status.SUCCESSFUL['code']:
        return None, None, status.ERR_NUM_OF_GUIDE_INCORRECT['code']
    # id 검출
    id, getId_status_code = getId(marking_tf_matrix)
    if getId_status_code != status.SUCCESSFUL['code']:
        return None, None, status.ERR_ID_MARKING_DUPLICATED['code']
    # safenum 검출    
    first_answerline_safenums, second_answerline_safenums, getSafeNums_status_code = getSafeNums(marking_tf_matrix)
    if getSafeNums_status_code != status.SUCCESSFUL['code']:
        return None, None, status.ERR_NUM_OF_SAFENUM_INCORRECT['code']
    # safecode 검출
    safecode, getSafeCode_status_code = getSafeCode(first_answerline_safenums, second_answerline_safenums)
    if getSafeCode_status_code != status.SUCCESSFUL['code']:
        return None, None, status.ERR_NO_MATCHING_SAFECODE['code']
    

    # 점 찍힌 이미지
    # cv2.imshow("Result", color_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # # 이진처리된 이미지
    # cv2.imshow("Result", preprocessed_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    # 첫번째 answerline 검출
    first_answerline_answers, is_first_answerline_safecode_valid = getFirstAnswerlineAnswers(marking_tf_matrix, first_answerline_safenums, safecode)
    # 두번재 answerline 검출
    second_answerline_answers, is_second_answerline_safecode_valid = getSecondAnswerlineAnswers(marking_tf_matrix, second_answerline_safenums, safecode)
    # safecode가 둘다 맞는지 체크
    is_safecode_valid = is_first_answerline_safecode_valid and is_second_answerline_safecode_valid


    return (id, is_safecode_valid, first_answerline_answers, second_answerline_answers, safecode), color_img, status.SUCCESSFUL['code']