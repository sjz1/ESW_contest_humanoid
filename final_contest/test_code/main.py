import cv2
import sys
import math
import cv2 as cv
import numpy as np
from time import sleep
from angle import detect_angle
from line_tracing.detect_ah_eh import detect_ah_eh

###라이브러리########
from line_tracing.final_center_sort_2022 import make_middle_flag
from only_for_blue_2022 import Blue_detect
from only_for_yellow_2022 import Yellow_detect


##############################[ main start ]##################################

#cap = cv2.VideoCapture(-1)   #카메라 키는 코드
W_View_size = 640
H_View_size = int(W_View_size / 1.333)
#만약 카메라 안켜지면 위에 카메라 cap 주석처리하고 FPS ~ print 까지 주석 풀어보기

FPS = 90  # PI CAMERA: 320 x 240 = MAX 90
try:
    cap = cv2.VideoCapture(0)  # 카메라 켜기  # 카메라 캡쳐 (사진만 가져옴)

    cap.set(3, W_View_size)
    cap.set(4, H_View_size)
    cap.set(5, FPS)

except:
    print('cannot load camera!')


# print("중앙정렬 코드 실행")
# flag = make_middle_flag(cap) # x: 30 왼: 32 중앙 31 오른쪽 33


# print("파란색 인식 코드 실행")
# check = Blue_detect(cap) #인식 o :41 ///  인식 x :40

# print("노란색 인식 코드 실행")
# check = Yellow_detect(cap) #인식 o :51 ///  인식 x :50

#print("ㅏ ㅓ ㅡ ㅣ 인식 코드 실행")
#flag = detect_ah_eh(cap) # x : // ㅓ : // ㅏ : // ㅣ :  // ㅡ :

print("회전정렬 코드 실행")
detect_angle(cap)