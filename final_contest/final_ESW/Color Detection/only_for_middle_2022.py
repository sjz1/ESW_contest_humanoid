import sys
import math
import cv2
import cv2 as cv
import numpy as np
from time import sleep 
cap = cv2.VideoCapture(0)   #저장된 영상파일 가져오기

#FPS = 90  # PI CAMERA: 320 x 240 = MAX 90

#try:
#    cap = cv2.VideoCapture(0)  # 카메라 켜기  # 카메라 캡쳐 (사진만 가져옴)
#
#    cap.set(3, W_View_size)
#    cap.set(4, H_View_size)
#    cap.set(5, FPS)
#
#except:
#    print('cannot load camera!')


#def find_the_middle(cap):
while (True):
    ret, src = cap.read() #영상파일 읽어드리기
    
    src = cv2.resize(src, (640, 360)) #가져올 파일, ()이미지크기

    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    #HSV H(Hue; 색조), S(Saturation; 채도), V(Value; 명도)
    #powerpoint에서 찾은값에 H는 1/2해줘야함
    #H:0~179 S:0~255 V:0~255
    
####################################################################
    yellow1 = np.array([16, 80,140])    #노랑색 최솟값
    yellow2 = np.array([90, 255,255])   #노랑색 최댓값
####################################################################
    mask_yellow = cv2.inRange(hsv, yellow1, yellow2) # 노랑최소최대값을 이용해서 maskyellow값지정
    
    res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow) # 노랑색만 추출하기
    
    srcs = res_yellow    #imgs에 추출한 노랑색 저장

    src2 = srcs.copy()
    h, w = srcs.shape[:2] #이미지 크기 조정

    imgray = cv2.cvtColor(srcs, cv2.COLOR_BGR2GRAY)
    dst = cv2.Canny(imgray, 200, 250, None, 3) #canny처리하기

#cv2.Canny(가져올파일,임계값1,임계값2,커널크기,L2그라디언트)
#임계값1이하에 포함된 가장자리는 가장자리에서 제외
#임계값2이상에 포함된 가장자리는 가장가지로 간주
#커널크기 : Aperture size
#L2그라디언트 :L2방식 √((dI/dx)^2+(dI/dx)^2)의 사용 유무 없으면
#L1 ∥dI/dx∥+∥dI/dy∥사용 간주


###################################################################

    cdst = cv2.cvtColor(dst, cv.COLOR_GRAY2BGR) #흑백 ---->컬러 선을 빨갛게 보이기 위
    cdstP = np.copy(cdst) #위에 컬러로 변환한 영상 저장
 
#    lines = cv2.HoughLines(dst, 1, np.pi / 180, 150, None, 0, 0) #허프변환
#
#    if lines is not None:
#        for i in range(0, len(lines)): #len()문자열의 길이구하기-허프변환으로 검출된 선의 개수 만큼
#            rho = lines[i][0][0]
#            theta = lines[i][0][1]
#            a = math.cos(theta)
#            b = math.sin(theta)
#            x0 = a * rho #이걸로 교차점에서 턴하는 값 지정가능
#            y0 = b * rho #이걸로 좌우 정할수 있는데 비슷한 맥락으로 나는 tan를 씀
#            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000* (a))) #시작점 
#            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a))) #종료점
#            pt3 = (int(x0),int(y0))
#            
#            cv.line(cdst, pt1, pt2, (0, 0, 255), 3, cv.LINE_AA) #라인그리기

    linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10) #확률적허프변환
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv.LINE_AA)

            if 200<l[0]<500 :
                print ("중앙 정렬 ok")
            elif l[0]<200 :
                print("Warning :: 우측으로 이동 ->중앙 정렬wrong")
            else:
                print(print("Warning :: 좌측으로 이동 ->중앙 정렬wrong"))

            if (l[2]-l[0]) == 0:
                continue
            else:
                grad = (l[3] - l[1])/(l[2]-l[0])
                grad_theta = (math.atan(grad))
                #print(grad_theta)
                if 0 <grad_theta < 1:
                    print("Warning :: 우회전 필요")

                elif -1 < grad_theta < 0:
                    print("Warning :: 좌회전 필요")

                else:
                    print("회전 각도 양호")

            sleep(0.1)


            
    cv.imshow("Original", src) #원본파일
    #cv.imshow("yellow_det", hsv) #노랑감지
    cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", res_yellow) #허프변환라인
    cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP) #확률적허프변환라인


    
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break




cap.release()
cv2.destroyAllWindows()
