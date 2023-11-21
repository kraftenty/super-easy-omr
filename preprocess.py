import cv2
import numpy as np

# 웹캠 화면 크기 설정
frame_width = 800
frame_height = 480

# 원근 변환 후 결과 이미지의 크기
output_height = 480
output_width = 680

def scan_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 흑백으로 변환
    edges = cv2.Canny(gray, 30, 80) # 엣지 검출
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 엣지 검출 결과에서 사각형 찾기

    for contour in contours:
        # 각 윤곽선을 근사화함
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 근사화된 윤곽선이 4개의 꼭지점을 가지면 사각형으로 간주
        if len(approx) == 4:
            # 사각형의 면적 계산
            area = cv2.contourArea(approx)

            # 사각형의 면적이 전체 화면 면적의 1/1.25 이상인 경우에만 연두색으로 채웁니다.
            if area >= (frame_width * frame_height) / 1.25:
                # cv2.drawContours(image, [approx], 0, (0, 255, 0), -1)  # 연두색으로 채움
                
                templi = []
                for point in approx:
                    x, y = point[0]
                    templi.append((x,y))
                
                # 이미지가 돌아가서 좌표차이가 너무 많이나면 그냥 리턴
                if abs(templi[3][1] - templi[0][1]) > 50:
                    return
                
                # 원근 변환 시작 ------
                # 원근 변환 전 4개의 점들
                c = 25 # 보정값(테두리 없애기)
                src_points = np.array([
                    [templi[3][0]-c, templi[3][1]+c],  # Top-Left
                    [templi[0][0]+c, templi[0][1]+c],  # Top-Right
                    [templi[1][0]+c, templi[1][1]-c],  # Bottom-Right
                    [templi[2][0]-c, templi[2][1]-c]   # Bottom-Left
                ], dtype=np.float32)

                # 원근 변환 될 프레임의 4개의 점들
                dest_points = np.array([
                    [0, 0],                        # Top-Left
                    [output_width, 0],             # Top-Right
                    [output_width, output_height], # Bottom-Right
                    [0, output_height]             # Bottom-Left
                ], dtype=np.float32)

                mtrx = cv2.getPerspectiveTransform(src_points, dest_points)
                captured_image = cv2.warpPerspective(image, mtrx, (output_width, output_height))
                # 원근 변환 완료 ------

                # 바이너리 이미지로 만들어서 저장하는 파트
                captured_gray_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
                global captured_binary_image
                captured_binary_image = cv2.adaptiveThreshold(captured_gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 17, 10) # 11,10
                return 9

def getProcessedImage():
    # 웹캠을 연결하고 크기 설정
    cap = cv2.VideoCapture(0)
    cap.set(3, frame_width)
    cap.set(4, frame_height)

    # 웹캠이 정상적으로 연결되었는지 확인
    if not cap.isOpened():
        print('Cannot Find WebCam')
        exit()

    while True:
        ret, frame = cap.read() # 웹캠에서 프레임을 읽어옴
        frame = cv2.flip(frame,1) # 좌우반전(거울모드)

        status = scan_image(frame)
        if status== 9:
            break

        cv2.imshow("WebCam", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # 이미지를 저장
    if captured_binary_image is not None:
        # cv2.imwrite("captured_image.png", captured_binary_image)
        return captured_binary_image

