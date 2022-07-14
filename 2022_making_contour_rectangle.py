

import cv2
import sys
import math
import cv2 as cv
import numpy as np
from time import sleep

yellow1 = np.array([0, 150, 110])  # 노랑색 최솟값
yellow2 = np.array([30, 255, 170])  # 노랑색 최댓값

W_View_size = 640
H_View_size = int(W_View_size / 1.777)
FPS = 90  # PI CAMERA: 320 x 240 = MAX 90

try:
    cap = cv2.VideoCapture(0)  # 카메라 켜기  # 카메라 캡쳐 (사진만 가져옴)

    cap.set(3, W_View_size)
    cap.set(4, H_View_size)
    cap.set(5, FPS)

except:
    print('cannot load camera!')

while (True):

   
    ret, frame = cap.read()  # 영상파일 읽어드리기

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_yellow = cv2.inRange(hsv, yellow1, yellow2)  # 노랑최소최대값을 이용해서 maskyellow값지정
    res_yellow = cv2.bitwise_and(frame, frame, mask=mask_yellow)  # 노랑색만 추출하기

    # 모폴로지
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dst = cv2.dilate(res_yellow, k)

    imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

    cam = cv2.GaussianBlur(imgray, (3, 3), 0)  # 가우시안 블러

    ret, cam_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이진화
    contours, hierarchy = cv2.findContours(cam_binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # 컨투어

    if len(contours) == 0:
        print("컨투어 0")

    else:
        contr = contours[0]
        x, y, w, h = cv2.boundingRect(contr)  # 최소한의 사각형 그려주는 함수
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        #print(" x = %d, w = %d" % (x, w))
        #print(' y = %d, h = %d' % (y, h))
        #print(w)
        if w == 640:
            print("T자 감지")
        else:
            
            if (x+ w) >= 640: #오른벽에 붙음
                if (h) == int(W_View_size / 1.777): # ㅏ
                    print("├")
                else:
                    print("┌")
            elif (x) <= 0: #오른쪽 벽에 붙음
                if (h) == int(W_View_size / 1.777): # ㅏ
                    print("┤")
                else:
                    print("┐")
            else:
                if h == int(W_View_size / 1.777):
                    print("직선 감지")
                else:
                    print("인식중")

    cv.imshow("Original", frame)  # 원본파일
    cv.imshow("yellow_det", res_yellow)  # 노랑감지

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
