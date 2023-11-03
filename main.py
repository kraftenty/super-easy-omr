import preprocess
import cv2
import numpy as np

img = preprocess.getProcessedImage()
cv2.imshow("img", img)

cv2.waitKey(0)
cv2.destroyAllWindows()