import cv2
import numpy as np

# 웹캠 화면 크기 설정
frame_width = 800
frame_height = 480

# 웹캠을 연결하고 크기 설정
cap = cv2.VideoCapture(0)
cap.set(3, frame_width)
cap.set(4, frame_height)

# 웹캠이 정상적으로 연결되었는지 확인
if not cap.isOpened():
    print("Cannot Find WebCam.")
    exit()

# 원근 변환 후 결과 이미지의 크기 (직사각형의 크기)
output_width = 720
output_height = 480


# 사각형을 찾아서 연두색으로 표시하며, 사각형 영역을 이미지로 저장하고 웹캠을 종료하는 함수
def find_and_save_rectangles(image):
    # 흑백으로 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 엣지 검출
    edges = cv2.Canny(gray, 30, 80)

    # 엣지 검출 결과에서 사각형 찾기
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # 각 윤곽선을 근사화함
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 근사화된 윤곽선이 4개의 꼭지점을 가지면 사각형으로 간주합니다.
        if len(approx) == 4:
            # 사각형의 면적 계산
            area = cv2.contourArea(approx)

            # 사각형의 면적이 전체 화면 면적의 1/1.25 이상인 경우에만 연두색으로 채웁니다.
            if area >= (frame_width * frame_height) / 1.25:
                # cv2.drawContours(image, [approx], 0, (0, 255, 0), -1)  # 연두색으로 채움

                templi = []
                # #꼭지점 좌표 표시
                for point in approx:
                    x, y = point[0]
                    templi.append((x,y))
                    cv2.putText(image, f"({x}, {y})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                print(templi)
                #원근 변환 파트
                src_points = np.array([
                    [templi[0][0], templi[0][1]],  # Top-Right
                    [templi[3][0], templi[3][1]],  # Top-Left
                    [templi[2][0], templi[2][1]],   # Bottom-Left
                    [templi[1][0], templi[1][1]]    # Bottom-Right
                ], dtype=np.float32)

                dest_points = np.array([
                    [0, 0],# Top-Left
                    [720, 0],# Top-Right
                    [720, 480],# Bottom-Right
                    [0, 480]# Bottom-Left
                ], dtype=np.float32)

                mtrx = cv2.getPerspectiveTransform(src_points, dest_points)

                result = cv2.warpPerspective(image, mtrx, (720, 480))
                cv2.imshow("cap", result)
         
                # # 사각형 영역을 이미지에 저장
                # x, y, w, h = cv2.boundingRect(approx)
                # global saved_image
                # saved_image = image[y:y+h, x:x+w]

                # # 웹캠 종료
                # cap.release()
                # cv2.destroyAllWindows()

                # return 9
                return

while True:
    # 웹캠에서 프레임을 읽어옴
    ret, frame = cap.read()

    status = find_and_save_rectangles(frame)
    if status== 9:
        break

    cv2.imshow("웹캠", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()

# # 이미지를 저장
# if result is not None:
#     cv2.imwrite("saved_image.png", result)