import cv2


WIDTH = 680
HEIGHT = 480
MATRIX_WIDTH = 19
MATRIX_HEIGHT = 12
SAFECODE_LINE = 18


def findGuides(contours, color_img):
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
    return upper_guides, right_guides


def doDot(upper_guides, right_guides, binary_img, color_img):
    if MATRIX_WIDTH != len(upper_guides) and MATRIX_HEIGHT != len(right_guides):
        print('[ERROR] The number of recognized guide points is incorrect.')
        print('        ERROR CODE 5')
        exit(5)
    ptr_matrix = [[0 for _ in range(MATRIX_WIDTH)] for _ in range(MATRIX_HEIGHT)]
    # 점 검사 핵심 루프
    for rightIdx, rightPtr in enumerate(right_guides):
        for upIdx, upperPtr in enumerate(upper_guides):
            # 바이너리 이미지의 해당 좌표에 마킹이 없으면
            if binary_img[rightPtr[1], upperPtr[0]] == 0:
                cv2.circle(color_img, (upperPtr[0], rightPtr[1]), 3, (0, 0, 255), -1)
                ptr_matrix[rightIdx][upIdx] = 0
            # 바이너리 이미지의 해당 좌표에 마킹이 있으면
            else:
                cv2.circle(color_img, (upperPtr[0], rightPtr[1]), 3, (0, 255, 0), -1)
                ptr_matrix[rightIdx][upIdx] = 1
    # DEBUG
    # for y in range(MATRIX_HEIGHT):
    #     for x in range(MATRIX_WIDTH):
    #         print(ptr_matrix[y][x], end='')
    #     print()
    return ptr_matrix


def getId(ptr_matrix):
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
    return id


def getSafeNums(ptr_matrix):
    first_answerline_safenums = []
    second_answerline_safenums = []
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
    
    return first_answerline_safenums, second_answerline_safenums


def getSafeCode(first_answerline_safenums, second_answerline_safenums):
    ########
    # SAFECODE
    # 0,7 / 0,7  : 1
    # 0,7 / 4,11 : 2
    # 4,11 / 0,7 : 3
    # 4,11 / 4,11: 4
    ########
    if first_answerline_safenums == [0,7] and second_answerline_safenums == [0,7]:
        return 1
    elif first_answerline_safenums == [0,7] and second_answerline_safenums == [4,11]:
        return 2
    elif first_answerline_safenums == [4,11] and second_answerline_safenums == [0,7]:
        return 3
    elif first_answerline_safenums == [4,11] and second_answerline_safenums == [4,11]:
        return 4
    else:
        return -1


def getFirstAnswerlineAnswers(ptr_matrix, first_answerline_safenums, safeCode):
    ## 첫번째 정답라인 정답 검출-----------------------------------------
    first_answerline_answers = []
    is_first_answerline_safecode_valid = True
    for y in range(0, 12):
        if y in first_answerline_safenums: # safecode 문항이면
            if ptr_matrix[y][8 + safeCode - 1] != 1:
                print('[ERROR] First answerline safecode is incorrect.')
                is_first_answerline_safecode_valid = False
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
    return first_answerline_answers, is_first_answerline_safecode_valid


def getSecondAnswerlineAnswers(ptr_matrix, second_answerline_safenums, safeCode):
    second_answerline_answers = []
    is_second_answerline_safecode_valid = True
    for y in range(0, 12):
        if y in second_answerline_safenums: # safecode 문항이면
            if ptr_matrix[y][13 + safeCode - 1] != 1:
                print('[ERROR] Second answerline safecode is incorrect.')
                is_second_answerline_safecode_valid = False
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
    return second_answerline_answers, is_second_answerline_safecode_valid


def getDetectedValues(preprocessedImg):
    # 이미지 이진화 (imtres = 이진화된 이미지)
    _, binary_img = cv2.threshold(preprocessedImg, 220, 255, cv2.THRESH_BINARY_INV)
    # 점 찾기
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 컬러로 변환한 이미지 (점찍기위해서)
    color_img = cv2.cvtColor(preprocessedImg, cv2.COLOR_GRAY2BGR)
    # 가이드 찾기
    upper_guides, right_guides = findGuides(contours, color_img)
    # 점 찍기
    ptr_matrix = doDot(upper_guides, right_guides, binary_img, color_img)
    # id 검출
    id = getId(ptr_matrix)
    # safenum 검출    
    first_answerline_safenums, second_answerline_safenums = getSafeNums(ptr_matrix)
    # safecode 검출
    safeCode = getSafeCode(first_answerline_safenums, second_answerline_safenums)
    # 첫번째 answerline 검출    
    first_answerline_answers, is_first_answerline_safecode_valid = getFirstAnswerlineAnswers(ptr_matrix, first_answerline_safenums, safeCode)
    # 두번재 answerline 검출
    second_answerline_answers, is_second_answerline_safecode_valid = getSecondAnswerlineAnswers(ptr_matrix, second_answerline_safenums, safeCode)
    


    # 점 찍힌 이미지
    cv2.imshow("Result", color_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    # 이진처리된 이미지
    cv2.imshow("Result", preprocessedImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

    is_safecode_valid = is_first_answerline_safecode_valid and is_second_answerline_safecode_valid
    return id, is_safecode_valid, first_answerline_answers, second_answerline_answers