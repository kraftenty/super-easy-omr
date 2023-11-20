import preprocess
import cv2
import numpy as np

WIDTH = 680
HEIGHT = 480

preprocessedImg = preprocess.getProcessedImage()
cv2.imshow("preprocessedImg", preprocessedImg)

# 이미지 이진화 (imtres = 이진화된 이미지)
_, imthres = cv2.threshold(preprocessedImg, 240, 255, cv2.THRESH_BINARY_INV)
# 점 찾기
contours, _ = cv2.findContours(imthres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# 컬러로 변환한 이미지 (점찍기위해서)
color_img = cv2.cvtColor(preprocessedImg, cv2.COLOR_GRAY2BGR)

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

# 디버그용
print(f'upper_guides={upper_guides}')
print(f'right_guides={right_guides}')

for upperPtr in upper_guides:
    for rightPtr in right_guides:
        # 점이 찍혀있는지 확인하고 싶어
        if imthres[rightPtr[1], upperPtr[0]] == 0:
            # 해당 좌표에 마킹이 없으면 빨간점
            cv2.circle(color_img, (upperPtr[0], rightPtr[1]), 3, (0, 0, 255), -1)
        else:
            # 해당 좌표에 마킹이 있으면 초록점
            cv2.circle(color_img, (upperPtr[0], rightPtr[1]), 3, (0, 255, 0), -1)

cv2.imshow("Result", color_img)
cv2.waitKey(0)
cv2.destroyAllWindows()


cv2.imshow("Result", preprocessedImg)
cv2.waitKey(0)
cv2.destroyAllWindows()