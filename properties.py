class status:
    SUCCESSFUL = {
        'code' : 0,
        'msg' : '[INFO] Successful.'
    }
    ERR_NUM_OF_GUIDE_INCORRECT = {
        'code' : 5,
        'msg' : '[ERROR] The number of guides is incorrect.'
    }
    ERR_ID_MARKING_DUPLICATED = {
        'code' : 6,
        'msg' : '[ERROR] ID marking is duplicated. ID is not readable.'
    }
    ERR_NUM_OF_SAFENUM_INCORRECT = {
        'code' : 7,
        'msg' : '[ERROR] The number of safenum is incorrect.'
    }
    ERR_NO_MATCHING_SAFECODE = {
        'code' : 8,
        'msg' : '[ERROR] No matching safecode.'
    }

class values:
    ANSWER_FILE_PATH = 'answer.json' # 정답 파일 경로

    FRAME_WIDTH = 800 # 웹캠 프레임 너비

    FRAME_HEIGHT = 480 # 웹캠 프레임 높이

    OUTPUT_WIDTH = 680 # 출력 이미지 너비

    OUTPUT_HEIGHT = 480 # 출력 이미지 높이

    CANVAS_WIDTH = OUTPUT_WIDTH * 2 # 캔버스 너비

    CANVAS_HEIGHT = int(OUTPUT_HEIGHT * 1.5) # 캔버스 높이

    LOG_INFO = '#00FF00' # 인포 로그 색상

    LOG_ERR = '#FF0000' # 에러 로그 색상