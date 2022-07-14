import cv2
import sys
import math
import cv2 as cv
import numpy as np
from time import sleep 
cap = cv2.VideoCapture(0)   #저장된 영상파일 가져오기


while (True):
    ret, src = cap.read() #영상파일 읽어드리기
 
    src = cv2.resize(src, (640, 360)) #가져올 파일, ()이미지크기

####################################################################


    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    #HSV H(Hue; 색조), S(Saturation; 채도), V(Value; 명도)
    #powerpoint에서 찾은값에 H는 1/2해줘야함
    #H:0~179 S:0~255 V:0~255

    yellow1 = np.array([16, 80,140])    #노랑색 최솟값
    yellow2 = np.array([90, 255,255])   #노랑색 최댓값

    mask_yellow = cv2.inRange(hsv, yellow1, yellow2) # 노랑최소최대값을 이용해서 maskyellow값지정
##    res_gray = cv2.cvtColor(mask_yellow, cv2.COLOR_BGR2GRAY)
##    ys,xs = np.where(res_gray>0)
##    print(ys,xs)
    
    res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow) # 노랑색만 추출하기
    

    
    srcs = res_yellow    #imgs에 추출한 노랑색 저장

    src2 = srcs.copy()
    h, w = srcs.shape[:2] #이미지 크기 조정

    imgray = cv2.cvtColor(srcs, cv2.COLOR_BGR2GRAY)
    dst = cv2.Canny(imgray, 50, 200, None, 3) #canny처리하기

###################################################################

    cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR) #흑백 ---->컬러 선을 빨갛게 보이기 위
    cdstP = np.copy(cdst) #위에 컬러로 변환한 영상 저장
 
    lines = cv.HoughLines(dst, 1, np.pi / 180, 150, None, 0, 0) #허프변환

    if lines is not None:
        for i in range(0, len(lines)): #len()문자열의 길이구하기-허프변환으로 검출된 선의 개수 만큼
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho #이걸로 교차점에서 턴하는 값 지정가능
            y0 = b * rho #이걸로 좌우 정할수 있는데 비슷한 맥락으로 나는 tan를 씀
            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000* (a))) #시작점 
            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a))) #종료점
            pt3 = (int(x0),int(y0))

            #print("t:",pt3)
            #print("x0y0",x0,y0)

            #abc(pt1, pt2)
            #print("1",pt1)
            #print("2",pt2)
            
            

            
            cv.line(cdst, pt1, pt2, (0, 0, 255), 3, cv.LINE_AA) #라인그리기
            #try:
                #print("기울기",(int(y0 + 1000 * (a))-int(y0 - 1000 * (a)))/int(x0 + 1000 * (a))-int(x0 - 1000 * (a)))
                #print("pt1:",pt1)
                #print("pt3:",pt3)
            #except ZeroDivisionError:
                #print("기울기",0)

            
#########################################방향전환##########################################

            
        #turnway = math.tan(theta)
        #print(turnway)
        #if -0.6 < turnway < 0.6:
            #print("straight")
        #elif turnway > 0.6 :
            #print("left")
        #else  :
            #print("right")


#####################################################################################################

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

            sleep(0.05)


            
    cv.imshow("Original", src) #원본파일
    #cv.imshow("yellow_det", hsv) #노랑감지
    cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", res_yellow) #허프변환라인
    cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP) #확률적허프변환라인


    
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

#cv2.Canny(가져올파일,임계값1,임계값2,커널크기,L2그라디언트)
#임계값1이하에 포함된 가장자리는 가장자리에서 제외
#임계값2이상에 포함된 가장자리는 가장가지로 간주
#커널크기 : Aperture size
#L2그라디언트 :L2방식 √((dI/dx)^2+(dI/dx)^2)의 사용 유무 없으면
#L1 ∥dI/dx∥+∥dI/dy∥사용 간주



#cv2.line(img,pt1,pt2,color,thickness,linetype,shift)
#img이미지 파일 pt1시작점 좌표(x,y) pt2종료점 좌표(x,y)
#color(blue,green,red) thickness(선두께 default 1)
#lineType(선 종류 default cv.Line_8)
#Line_8 : 8 connected line , Line_4 : 4 connected line , Line_AA antialiased line
#shift fractional bit (default 0)


#허프변환
#cv2.HoughLines(image, rho, theta, threshold[, lines[, srn[, stn[, min_theta[, max_theta]]]]])
#image - Output of the edge detector,회색조 이미지여야
#rho - r값의 범위 (0~1 실수) 주로 1 사용  , 매개변수의 해상도
#theta -θ값의 범위 (0~180 정수) pi/180=1
#threshold - 만나는 점의 기준, 숫자가 작으면 많은 선이 검출되지만 정확도가 떨어짐
#srn 및 stn 기본 매개 변수는 0



#확률적허프변환
    #linesP = cv.HoughLinesP (dst, 1, np.pi / 180, 50, None , 50, 10)
    #dst-  edge 변환의 출력 (회색이여야함)
    #lines: A vector that will store the parameters (xstart,ystart,xend,yend) of the detected lines
    #rho : The resolution of the parameter r in pixels. We use 1 pixel.
    #theta: The resolution of the parameter θ in radians. We use 1 degree (CV_PI/180)
    #threshold: 선을 감지하기위한 최소 교차 수 
    #minLinLength: 선을 형성 할 수있는 최소 포인트 수. 이 포인트 수보다 적은 라인은 무시됩니다..
    #maxLineGap: 같은 선에서 고려할 두 점 사이의 최대 간격.


#def abc(pt1,pt2):
    
