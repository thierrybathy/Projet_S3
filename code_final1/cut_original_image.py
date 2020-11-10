import cv2
import numpy as np

img = cv2.imread("F:\projet_S5\source\Mr_clair.tif")
img1 = img[4000:5000, 4000:5000]
print("aaa")
cv2.imshow("sss", img1)
cv2.waitKey(0)
print("bbb")
cv2.imwrite("F:\projet_S5\source\part2_Mr_clair.tif", img1, [cv2.IMWRITE_PNG_COMPRESSION, 0])
