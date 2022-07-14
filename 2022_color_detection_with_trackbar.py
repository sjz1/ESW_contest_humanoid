import cv2
import sys
import math
import cv2 as cv
import numpy as np
from time import sleep


#trackbar callback fucntion to update HSV value
def callback(x):
	global H_low,H_high,S_low,S_high,V_low,V_high
	#assign trackbar position value to H,S,V High and low variable
	H_low = cv2.getTrackbarPos('low H','controls')
	H_high = cv2.getTrackbarPos('high H','controls')
	S_low = cv2.getTrackbarPos('low S','controls')
	S_high = cv2.getTrackbarPos('high S','controls')
	V_low = cv2.getTrackbarPos('low V','controls')
	V_high = cv2.getTrackbarPos('high V','controls')


#create a seperate window named 'controls' for trackbar
cv2.namedWindow('controls',2)
cv2.resizeWindow("controls", 550,10);


#global variable
H_low = 0
H_high = 179
S_low= 0
S_high = 255
V_low= 0
V_high = 255

#create trackbars for high,low H,S,V 
#create trackbars for high,low H,S,V 
cv2.createTrackbar('low H','controls',0,255,callback)
cv2.createTrackbar('high H','controls',225,225,callback)

cv2.createTrackbar('low S','controls',0,255,callback)
cv2.createTrackbar('high S','controls',255,255,callback)

cv2.createTrackbar('low V','controls',0,255,callback)
cv2.createTrackbar('high V','controls',255,255,callback)


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
    lower =  np.array([H_low, S_low, V_low])
    higher = np.array([H_high, S_high, V_high])

   
    ret, frame = cap.read()  # 영상파일 읽어드리기

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_color = cv2.inRange(hsv, lower, higher)  # 노랑최소최대값을 이용해서 maskyellow값지정
    res_color = cv2.bitwise_and(frame, frame, mask=mask_color)  # 노랑색만 추출하기

    # 모폴로지
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dst = cv2.dilate(res_color, k)

    imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

    cam = cv2.GaussianBlur(imgray, (3, 3), 0)  # 가우시안 블러

    ret, cam_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이진화
    contours, hierarchy = cv2.findContours(cam_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 컨투어

    if len(contours) == 0:
        print("정상 상태")

    else:
        contr = contours[0]
        #rect = cv2.minAreaRect(contr)
        x, y, w, h = cv2.boundingRect(contr)  # 최소한의 사각형 그려주는 함수
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        #box = cv2.boxPoints(rect)   # 중심점과 각도를 4개의 꼭지점 좌표로 변환
        #box = np.int0(box)          # 정수로 변환
        #cv2.drawContours(frame, [box], -1, (0,255,0), 3)
        print("지정색깔 감지"," 좌표 : (", x+0.5*w, " , ",y+0.5*h ,")")


    cv.imshow("Original", frame)  # 원본파일
    cv.imshow("detection range", res_color)  # 노랑감지

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()


#cv2.drawContours(이미지, [윤곽선], 윤곽선 인덱스, (B, G, R), 두께, 선형 타입)
