import cv2
import numpy as np


def scan_image(image, frame_width, frame_height, output_width, output_height):
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
                captured_binary_image = cv2.adaptiveThreshold(captured_gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 17, 10) # 11,10
                return captured_binary_image
    return None
    