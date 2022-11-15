import platform
from re import A, S
from tkinter import E, N, W
import numpy as np
import argparse
import cv2
import cv2 as cv
import serial
import time
import sys
from threading import Thread
import math
import pytesseract
from time import sleep
from imutils.perspective import four_point_transform
from imutils.contours import sort_contours
import imutils
serial_use = 1

serial_port =  None
Read_RX =  0
receiving_exit = 1
threading_Time = 0.01

#----------------------------------------------- 
#----------------------------------------------- 

# 확인해야하는 글자 개수 -> 이에 따라 라인트레이싱 방법 달라짐
global Letter_cnt
Letter_cnt = 3

# 송/수신 데이터 값
START = 0

############## 방향 인식 ##############
Arrow_detect = 1
Arrow_no = 10
Arrow_left = 11
Arrow_right = 12

############## 글자 인식 ##############
Alpha_detect = 2
Alpha_no= 20
Alpha_E = 21
Alpha_W = 22
Alpha_S = 23
Alpha_N = 24
Alpha_A = 25
Alpha_C = 26
Alpha_B = 27
Alpha_D = 28

############## 라인트레이싱 ##############
Line_detect = 3
Line_no = 30
Line_mid = 31
Line_left = 32
Line_right = 33
Line_threeway_no = 34
Line_threeway_yes = 35
# 마지막 부분의 라인트레이싱에서 사용되는 변수
# 앵글값에 따라 위의 Line_left, Line_right보다 조금씩 움직이기
Line_angle_mid = 36
Line_angle_left = 37
Line_angle_right = 38

############## 파란색 인식 ##############
Blue_detect = 4
Blue_no = 40
Blue_yes = 41

############## 노란색 인식 ##############
Yellow_detect = 5
Yellow_no = 50
Yellow_yes = 51

############## 검정색 인식 ##############
Black_detect = 6
Black_no = 60
Black_yes = 61

############## 초록색 인식 ##############
Green_detect = 7
Green_no = 70
Green_yes = 71

############## 빨간색 인식 ##############
Red_detect = 8
Red_no = 80
Red_yes = 81

############## 시민 인식 ##############
BluePerson_detect = 9
BluePerson_detect_no = 90
BluePerson_detect_mid = 91
BluePerson_detect_left = 92
BluePerson_detect_right = 93
BluePerson_detect_grap = 94
BluePerson_detect_no_grap = 95

#----------------------------------------------- 
#----------------------------------------------- 

#***********************Setting Part ****************************#

#color
yellow1 = np.array([16, 80,140])    #min of yellow
yellow2 = np.array([90, 255,255])   #max of yellow
yellow_chance = 2 #sensitive (default = 2)

bell_yellow1 =  np.array([16, 80,140]) 
bell_yellow2 = np.array([90, 255,255])
bell_yellow_chance = 2 #sensitive (default = 2)

blue1 = np.array([91, 159,81])    #min of blue (default : [120-10, 30,30])
blue2 = np.array([141, 255,255])   #max of blue (default : [120+10, 255,255])
blue_chance = 2 #sensitive (default = 2)

green1= np.array([72, 61,20]) 
green2 = np.array([86, 255,127]) 
green_chance= 2 #sensitive (default = 2)

black1 = np.array([0, 120,110])    #min of blue (default : [120-10, 30,30])
black2 = np.array([50, 136,136])   #max of blue (default : [120+10, 255,255])
black_chance = 2 #sensitive (default = 2)

grap_blue_color1 = np.array([91, 159,81])    #min of blue (default : [120-10, 30,30])
grap_blue_color2 = np.array([141, 255,255])   #max of blue (default : [120+10, 255,255])
grap_sensitive = 5 #voting count (default = 5)
is_near = 180 * 150 #blue is far or near  (default : )

where_blue1 = np.array([91, 159,81])    #min of blue (default : [120-10, 30,30])
where_blue2   = np.array([141, 255,255])   #max of blue (default : [120+10, 255,255])
where_blue_center_sensitive = 100 #area: center_sensitive x 2 (default = 100)
where_blue_sensitive = 5 #voting count (default = 5)
########################################################################
########################################################################

#linetrace
###0~ 640 기준 250~350
mid_yellow1 = np.array([16, 80,140])    #min of yellow (default = [16, 80,140]) => line trace
mid_yellow2 = np.array([90, 255,255])   #max of yellow (default = [90, 255,255]) => line trace
center_sensitive = 100 #area: center_sensitive x 2 (default = 100)
mid_sensitive = 5 #voting count (default = 5)

ah_eh_sensitive = 3 #voting count (default = 5)
ah_eh_rev_sensitive = 40 #ㅓ,ㅏ판단할 때 둔감도(default 20)


angle_yellow1 = np.array([16, 80,140])
angle_yellow2= np.array([90, 255,255])
right_angle = 1 # (정상 최대 오른각도   default = 1)
left_angle = -1  #right_angle * (-1) 권장

#----------------------------------------------- 
#----------------------------------------------- 
def make_scan_image(image, width, ksize=(5,5), min_threshold=75, max_threshold=200):
    image_list_title = []
    image_list = []

    org_image = image.copy()
    image = imutils.resize(image, width=width)
    ratio = org_image.shape[1] / float(image.shape[1])

    # 이미지를 grayscale로 변환하고 blur를 적용
    # 모서리를 찾기위한 이미지 연산
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, ksize, 0)
    edged = cv2.Canny(blurred, min_threshold, max_threshold)

    image_list_title = ['gray', 'blurred', 'edged']
    image_list = [gray, blurred, edged]

    # contours를 찾아 크기순으로 정렬
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    findCnt = None

    # 정렬된 contours를 반복문으로 수행하며 4개의 꼭지점을 갖는 도형을 검출
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    # contours가 크기순으로 정렬되어 있기때문에 제일 첫번째 사각형을 영역으로 판단하고 break
        
        if len(approx) == 4:
            findCnt = approx
            break

    # 만약 추출한 윤곽이 없을 경우 오류
    if findCnt is None:
        #raise Exception(("Could not find outline."))
        return org_image
    output = image.copy()
    cv2.drawContours(output, [findCnt], -1, (0, 255, 0), 2)

    image_list_title.append("Outline")
    image_list.append(output)

    # 원본 이미지에 찾은 윤곽을 기준으로 이미지를 보정
    transform_image = four_point_transform(org_image, findCnt.reshape(4, 2) * ratio)

    #plt_imshow(image_list_title, image_list)
    #plt_imshow("Transform", transform_image)

    return transform_image
#-----------------------------------------------
############## 방향 인식(제어보드로부터 Arrow_detect 수신) ##############
def arrow(cap):
    #contouring 
    left=0
    right=0
    noway=0
    
    for i in range(30):
        ret, src=cap.read()
        img_gray=cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
        ret,img_binary=cv2.threshold(img_gray,50,255,0)
        contours,hierachy=cv2.findContours(img_binary,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

        #최소 사각형 크기 제한
        maxrect=200
        
        for cnt in contours:

            try:
                hull =cv2.convexHull(cnt,returnPoints=False)
                defects=cv2.convexityDefects(cnt,hull)
            except:
                pass
                    
            x,y,w,h=cv2.boundingRect(cnt)
            
            #max rectangle size limit 가장 큰 사각형을 뽑아 연산을 위함
            if w*h>maxrect and w*h<150000 and x>10 and y>10:
                cv2.drawContours(src,[cnt],0,(0,255,0),3)
                cv2.rectangle(src,(x,y),(x+w,y+h),(0,255,0),2)
                maxrect=w*h
                
                # center spot Point 중심점 찍기
                M=cv2.moments(cnt)
                try:
                    cx=int(M['m10']/M['m00'])
                    cy=int(M['m01']/M['m00'])
                except:
                    pass
                # rectangle inner point count 사각형 내부 점찍기
                try:
                    #방향을 위한 변수 direct
                    direct=0
                    for i in range(defects.shape[0]):
                        s,e,f,d=defects[i,0]
                        start =tuple(cnt[s][0])
                        end=tuple(cnt[e][0])
                        far=tuple(cnt[f][0])
                        
                        if d>500:
                            #꼭짓점 찍기
                            cv2.circle(src,far,5,[0,0,255],-1)
                            point_x,point_y=far
                            
                            #far is point location
                            #사각형 외부의 점은 무시
                            if point_x<x or point_x>x+w or point_y<y or point_y>y+h:
                                continue
                            else:
                                #point located left from center 중심 왼쪽에 점이 위치할 때
                                if cx>point_x:
                                    direct+=1
                                #point located right from center 중심 오른쪽에 점이 위치할 때
                                else:
                                    direct-=1
                    #many points located on left 왼쪽에 많을 때
                    if direct>0:
                        left+=1
                    elif direct==0:
                        noway+=1                  
                    #many points located on right 오른쪽에 많을때
                    else:
                        right+=1
                                            
                except:
                    pass
                
        try:
            #중심점 찍기
            cv2.circle(src,(cx,cy),10,(0,0,255),-1)
        except:
            pass
        
    if right>left and right>noway :
        #print("right arrow")
        flag = Arrow_right
  
    elif left>right and left>noway :
        #print("left arrow")
        flag = Arrow_left
       
    else :
        #print("no arrow")
        flag = Arrow_no

    return flag

#-----------------------------------------------
############## 글자 인식(제어보드로부터 Alpha_detect 수신) ##############
def letterdetect(cap):
    global Letter_cnt
    charlist=[]
    for i in range(10):
        ret, src = cap.read()
        image=np.array(src)
        options="--psm 7"
        src = make_scan_image(image, width=200, ksize=(5, 5), min_threshold=20, max_threshold=100)
        imgchar=pytesseract.image_to_string(src,config=options)
        charlist.append(imgchar)
    needletters=['N','W','w','E','S','s','A','B','C','c','D']
    answer=' '
    for j in charlist:
        for needletter in needletters:
            if j.find(needletter) >= 0:
            #찾은 문자를 answer에 저장
                answer=needletter

    if  answer==' ':
        #문자를 찾지못함
        #print("No detected")
        flag = Alpha_no

    else:
        # 글자 확인 -> 확인해야하는 글자의 수 하나 감소
        
        Letter_cnt -= 1

        #answer에 찾은 문자 저장되있음
        if answer.find('N') >= 0 :
            #print("N detected")
            flag = Alpha_N
            
        elif answer.find('W')>=0 or answer.find('w')>=0:
            #print("W detectded")
            flag = Alpha_W
           
        elif answer.find('E')>=0:
            #print("E detectded")
            flag = Alpha_E
  
        elif answer.find('S')>=0 or answer.find('s')>=0:
            flag = Alpha_S
            #print("S detectded")
          
        elif answer.find('A')>=0:
            #print("A detectded")
            flag = Alpha_A
            
        elif answer.find('B')>=0:
            #print("B detectde")
            flag = Alpha_B

        elif answer.find('C')>=0 or answer.find('c')>=0:
            #print("C detectde")
            flag = Alpha_C

        elif answer.find('D')>=0:
            #print("D detectde")
            flag = Alpha_D

    return flag
            
#-----------------------------------------------
############## 라인 트레이싱_중앙 정렬(제어보드로부터 Line_detect 수신 -> 첫번째) ##############
def make_middle_flag(cap, mid_yellow1,mid_yellow2,center_sensitive,mid_sensitive) -> 3:
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    right_flag = 320+center_sensitive
    left_flag = 320-center_sensitive
    ################[Can't,  Left,  Center,  Right]#########################
    lst_sensitive = [0,      0,     0,       0]
    past = 0
    sensitive = mid_sensitive

    while(True):
        _, src = cap.read() #영상파일 읽어드리기

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        yellow1 = mid_yellow1
        yellow2 = mid_yellow2
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2)  # 노랑최소최대값을 이용해서 maskyellow값지정
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow)  # 노랑색만 추출하기

        k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dst = cv2.dilate(res_yellow, k)
        imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        cam = cv2.GaussianBlur(imgray, (3, 3), 0)  # 가우시안 블러
        _, cam_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이진화
        contours, _ = cv2.findContours(cam_binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # 컨투어


        while (sensitive not in lst_sensitive):
            if len(contours) == 0:
                if past == 0: #연속된다면
                    lst_sensitive[0] += 1
                else: #연속이 아니라면
                    lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                    past = 0 #past를 바꿔주고
                    lst_sensitive[0] += 1
            else:
                contr = contours[0]
                x, y, w, h = cv2.boundingRect(contr)  # 최소한의 사각형 그려주는 함수
                cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 0), 3)
                mid_x = x + (w/2)
                
                #Center => 2
                if mid_x > left_flag and mid_x < right_flag: 
                    if past == 2: #연속된다면
                        lst_sensitive[2] += 1
                    else: #past = 1,2 연속이 아니였다면
                        lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                        past = 2 #past를 바꿔주고
                        lst_sensitive[2] += 1
                        
                #Right
                elif mid_x >= right_flag:
                    if past == 3: #연속된다면
                        lst_sensitive[3] += 1
                    else:
                        lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                        past = 3
                        lst_sensitive[3] += 1
                #Left
                else:
                    if past == 1: #연속된다면
                        lst_sensitive[1] += 1
                    else:
                        lst_sensitive = [0,   0,     0,    0]
                        past = 1
                        lst_sensitive[1] += 1
                #print(lst_sensitive)
        flag = lst_sensitive.index(sensitive)
        ################[Can't,  Left,  Center,  Right]#########################
        if flag == 0:
            #print("Can't detect Yellow !!")
            flag =Line_no
        

        elif flag == 1:
            #print("It's Left")
            flag = Line_left
        
        elif flag == 2:
            #print("Robot on Center")
            flag = Line_mid

        else: #3
            #print("It's Right")
            flag = Line_right
        
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        #print(flag)
        ######################contest#######################
        return flag
        #####################################################

        cv.imshow("Original", src) #원본 화면
        #cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.08)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()  
''' x: Line_no(30) /  왼: Line_left(32) / 중앙 Line_mid(31) 오른쪽 Line_right(33) '''
    
#-----------------------------------------------
############## 라인 트레이싱_세갈래길 인식(제어보드로부터 Line_detect 수신 -> 두번째) ##############
def detect_ah_eh(cap,mid_yellow1,mid_yellow2,ah_eh_sensitive,ah_eh_rev_sensitive) -> 3:
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    yellow1 = mid_yellow1
    yellow2 = mid_yellow2
    rev_sensitive = ah_eh_rev_sensitive
    sensitive = ah_eh_sensitive

    ################[Can't,  Left,  Center,  Right]#########################

    while(True):
        ############### [X,      ㅓ,     ㅣ,     ㅏ]
        lst_sensitive = [0,       0,      0,      0]
        past = 0
        _, src = cap.read() #영상파일 읽어드리기

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2)  # 노랑최소최대값을 이용해서 maskyellow값지정
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow)  # 노랑색만 추출하기

        k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dst = cv2.dilate(res_yellow, k)
        imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        cam = cv2.GaussianBlur(imgray, (3, 3), 0)  # 가우시안 블러
        ret, cam_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이진화
        contours, hierarchy = cv2.findContours(cam_binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # 컨투어


        while (sensitive not in lst_sensitive):
            if len(contours) == 0:
                if past == 0: #연속된다면
                    lst_sensitive[0] += 1
                else: #연속이 아니라면
                    lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                    past = 0 #past를 바꿔주고
                    lst_sensitive[0] += 1
            else:
                contr = contours[0]
                x, y, w, h = cv2.boundingRect(contr)  # 최소한의 사각형 그려주는 함수
                cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 0), 3)
                
                #ㅓ => 1
                if x <= 0+rev_sensitive: 
                    if past == 1: #연속된다면
                        lst_sensitive[1] += 1
                        
                    else: #past 연속이 아니였다면
                        lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                        past = 1 #past를 바꿔주고
                        lst_sensitive[1] += 1
                        
                        
                #ㅏ => 3
                elif x + w >= 630-rev_sensitive:
                    if past == 3: #연속된다면
                        lst_sensitive[3] += 1
                        
                    else:
                        lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                        past = 3
                        lst_sensitive[3] += 1
                #ㅣ -> 2
                else:
                    if past == 2: #연속된다면
                        lst_sensitive[2] += 1
                    else:
                        lst_sensitive = [0,   0,     0,    0]
                        past = 2
                        lst_sensitive[2] += 1
            #print(lst_sensitive)
        flag = lst_sensitive.index(sensitive)
        ################[Can't,  Left,  Center,  Right]#########################
        sleep(1)
        if flag == 0:
            #print("Can't detect Yellow !!")
            flag =Line_no
        

        elif flag == 1:
            #print("I Guess it's ㅓ")
            flag = Line_threeway_yes
        
        elif flag == 2:
            #print("I Guess it's ㅣ")
            flag = Line_threeway_no


        else: #3
            #print("I Guess it's ㅏ")
            flag = Line_threeway_yes
        
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        #print(flag)
        ######################contest#######################
        return flag
        #####################################################

        cv.imshow("Original", src) #원본 화면
        cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.01)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''x: Line_no(30)  ㅓㅏ: Line_threeway_yes(35) / ㅓㅏx :Line_threeway_no(34) '''

#-----------------------------------------------
############## 라인 트레이싱_각도 정렬(제어보드로부터 Line_detect 수신 -> 세번째) ##############
#############################[add part ] ##############################
def detect_angle(cap, angle_yellow1, angle_yellow2,right_angle,left_angle) -> 3:
    yellow1,yellow2 = angle_yellow1, angle_yellow2
    while (True):
        _ , src = cap.read() #영상파일 읽어드리기
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2) # 노랑최소최대값을 이용해서 maskyellow값지정      
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow) # 노랑색만 추출하기     
        srcs = res_yellow    #imgs에 추출한 노랑색 저장
        imgray = cv2.cvtColor(srcs, cv2.COLOR_BGR2GRAY)
        dst = cv2.Canny(imgray, 50, 200, None, 3) #canny처리하기
        cdstP = cv.cvtColor(dst, cv.COLOR_GRAY2BGR) #흑백 ---->컬러 선을 빨갛게 보이기 위
        linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10) #확률적허프변환
        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv.LINE_AA)
                if (l[2]-l[0]) == 0:
                    continue
                else:
                    grad = (l[3] - l[1])/(l[2]-l[0])
                    grad_theta = (math.atan(grad))
                    print(grad_theta)
                if 0 <grad_theta < right_angle:
                    print("Warning :: 우회전 필요")
                    flag = Line_angle_right

                elif left_angle < grad_theta < 0:
                    print("Warning :: 좌회전 필요")
                    flag = Line_angle_left

                else:
                    print("회전 각도 양호")
                    flag = Line_angle_mid
                return flag

                sleep(0.3)
        else:
            print("라인인식 못함")
            flag = Line_no
            return flag


                
        #cv.imshow("Original", src) #원본파일
        #cv.imshow("yellow_det", hsv) #노랑감지
        #cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP) #확률적허프변환라인
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break


    cap.release()
    cv2.destroyAllWindows()
''' 똑바름 : Line_angle_mid(36) / 좌회전 필요 : Line_angle_left(37) / 우회전 필요 : Line_angle_right(38) / Line_no = 30'''

#-----------------------------------------------
############## 시민 인식 (제어보드로부터 BluePerson_detect 수신) ##############
# 시민 위치
def where_is_blue(cap,where_blue1,where_blue2,where_blue_center_sensitive,) -> 9:
    #yellow라 이름 되어 있지만 blue 입니다
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    yellow1 = where_blue1    #min of blue (default : [120-10, 30,30])
    yellow2 = where_blue2   #max of blue (default : [120+10, 255,255])
    right_flag = 320+where_blue_center_sensitive
    left_flag = 320-where_blue_center_sensitive
    ################[Can't,  Left,  Center,  Right]#########################
    lst_sensitive = [0,      0,     0,       0]
    past = 0


    while(True):
        _, src = cap.read() #영상파일 읽어드리기

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2)  # 노랑최소최대값을 이용해서 maskyellow값지정
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow)  # 노랑색만 추출하기

        k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dst = cv2.dilate(res_yellow, k)
        imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        cam = cv2.GaussianBlur(imgray, (3, 3), 0)  # 가우시안 블러
        ret, cam_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이진화
        contours, hierarchy = cv2.findContours(cam_binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # 컨투어


        while (where_blue_sensitive not in lst_sensitive):
            if len(contours) == 0:
                if past == 0: #연속된다면
                    lst_sensitive[0] += 1
                else: #연속이 아니라면
                    lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                    past = 0 #past를 바꿔주고
                    lst_sensitive[0] += 1
            else:
                contr = contours[0]
                x, y, w, h = cv2.boundingRect(contr)  # 최소한의 사각형 그려주는 함수
                cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 0), 3)
                mid_x = x + (w/2)
                
                #Center => 2
                if mid_x > left_flag and mid_x < right_flag: 
                    if past == 2: #연속된다면
                        lst_sensitive[2] += 1
                    else: #past = 1,2 연속이 아니였다면
                        lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                        past = 2 #past를 바꿔주고
                        lst_sensitive[2] += 1
                        
                #Right
                elif mid_x >= right_flag:
                    if past == 3: #연속된다면
                        lst_sensitive[3] += 1
                    else:
                        lst_sensitive = [0,   0,     0,    0]#초기화시켜주고
                        past = 3
                        lst_sensitive[3] += 1
                #Left
                else:
                    if past == 1: #연속된다면
                        lst_sensitive[1] += 1
                    else:
                        lst_sensitive = [0,   0,     0,    0]
                        past = 1
                        lst_sensitive[1] += 1
                print(lst_sensitive)
        flag = lst_sensitive.index(where_blue_sensitive)
        ################[Can't,  Left,  Center,  Right]#########################
        if flag == 0:
            print("Can't detect blue !!")
            flag =BluePerson_detect_no
        

        elif flag == 1:
            print("It's Left")
            flag = BluePerson_detect_left
        
        elif flag == 2:
            print("Robot on Center")
            flag = BluePerson_detect_mid

        else: #3
            print("It's Right")
            flag = BluePerson_detect_right
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        #print(flag)
        ######################contest#######################
        return flag
        #####################################################

        cv.imshow("Original", src) #원본 화면
        #cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.08)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''인식 x: BluePerson_detect_no(90) / 왼: BluePerson_detect_left(92)
   중앙 BluePerson_detect_mid(91) / 오른쪽 BluePerson_detect_right(93)'''

# 시민 그랩 여부
def grap(cap,grap_blue_color1,grap_blue_color2,is_near,grap_sensitive) -> 9:
    #yellow라 이름 되어 있지만 blue 입니다
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    yellow1 = grap_blue_color1
    yellow2 = grap_blue_color2

    ################[Can't, near,  far]#########################
    

    while(True):
        lst_sensitive = [0,      0,     0]
        past = 0
        _, src = cap.read() #영상파일 읽어드리기

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2)  # 노랑최소최대값을 이용해서 maskyellow값지정
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow)  # 노랑색만 추출하기

        k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dst = cv2.dilate(res_yellow, k)
        imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        cam = cv2.GaussianBlur(imgray, (3, 3), 0)  # 가우시안 블러
        _, cam_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이진화
        contours, _ = cv2.findContours(cam_binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # 컨투어


        while (grap_sensitive not in lst_sensitive):
            if len(contours) == 0:
                if past == 0: #연속된다면
                    lst_sensitive[0] += 1
                else: #연속이 아니라면
                    lst_sensitive = [0,   0,     0]#초기화시켜주고
                    past = 0 #past를 바꿔주고
                    lst_sensitive[0] += 1
            else:
                contr = contours[0]
                x, y, w, h = cv2.boundingRect(contr)  # 최소한의 사각형 그려주는 함수
                cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 0), 3)
                mid_x = x + (w/2)

                #grap
                
                if w * h >= is_near: 
                    if past == 1: #연속된다면
                        lst_sensitive[1] += 1
                    else: #past = 1,2 연속이 아니였다면
                        lst_sensitive = [0,    0,   0] #초기화시켜주고
                        past = 1 #past를 바꿔주고
                        lst_sensitive[1] += 1

                else: #멀때 
                    if past == 2: #연속된다면
                        lst_sensitive[2] += 1
                    else: #past = 1,2 연속이 아니였다면
                        lst_sensitive = [0,    0,   0] #초기화시켜주고
                        past = 2 #past를 바꿔주고
                        lst_sensitive[2] += 1
                
                #print(lst_sensitive)
        print(w*h)
        flag = lst_sensitive.index(grap_sensitive)
        ################[Can't,  Left,  Center,  Right, grap]#########################
        if flag == 0:
            print("Can't detect blue !!")
            flag =BluePerson_detect_no
        

        elif flag == 1:
            print("Grap the fucking person!!!!")
            #정현
            flag = BluePerson_detect_grap
        
        else: #flag == 2:
            print("It's far to grap")
            #정현
            flag = BluePerson_detect_no_grap
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        #print(flag)
        ######################contest#######################
        return flag
        #####################################################
        cv.imshow("Original", src) #원본 화면
        cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''x: BluePerson_detect_no(90) / 잡기: BluePerson_detect_grap(94) 
   멀다 : BluePerson_detect_no_grap(95)'''
    
#-----------------------------------------------
############## 파란색 인식(제어보드로부터 Blue_detect 수신) ##############
def Blue_color_detect(cap, blue1, blue2, blue_chance) -> 4:
    count_blue = 0

    while (True):
        _, src = cap.read() #영상파일 읽어드리기

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        #HSV H(Hue; 색조), S(Saturation; 채도), V(Value; 명도)
        #powerpoint에서 찾은값에 H는 1/2해줘야함


        mask_blue = cv2.inRange(hsv, blue1, blue2) # 노랑최소최대값을 이용해서 maskyellow값지정
        
        res_blue = cv2.bitwise_and(src, src, mask=mask_blue) # 노랑색만 추출하기
        switch = 0

        for metrix in res_blue: # row_level
            switch += sum(metrix)

        if sum(switch) == 0:
            if count_blue > blue_chance:
                count_blue = 0
                print("no blue detect")
                check = Blue_no
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_blue += 1
        else:
            if count_blue < blue_chance*(-1):
                count_blue = 0
                print("Complete Detect Blue!")
                check = Blue_yes
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_blue -= 1
        sleep(0.01)
        #화면 띄우기
        #cv.imshow("Original", src) #원본 화면
        #cv.imshow("Detection of blue", res_blue) #원본 화면
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break



    cap.release()
    cv2.destroyAllWindows()
'''인식 o :Blue_yes(41) ///  인식 x :Blue_no(40)'''

    
#-----------------------------------------------
############## 노란색 인식(제어보드로부터 Yellow_detect 수신) ##############
def Yellow_bell_detect(cap,bell_yellow1,bell_yellow2,bell_yellow_chance) -> 5:
    
    #만약 카메라 안켜지면 위에 카메라 cap 주석처리하고 FPS ~ print 까지 주석 풀어보기
    count_yellow = 0

    ####################################################################

    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    yellow1=bell_yellow1
    yellow2=bell_yellow2
    yellow_chance = bell_yellow_chance

    while (True):

        _, src = cap.read() #영상파일 읽어드리기

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        #HSV H(Hue; 색조), S(Saturation; 채도), V(Value; 명도)
        #powerpoint에서 찾은값에 H는 1/2해줘야함
        #H:0~179 S:0~255 V:0~255

        mask_yellow = cv2.inRange(hsv, yellow1, yellow2) # 노랑최소최대값을 이용해서 maskyellow값지정
        
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow) # 노랑색만 추출하기
        switch = 0

        for metrix in res_yellow: # row_level
            switch += sum(metrix)

        if sum(switch) == 0:
            if count_yellow > yellow_chance:
                count_yellow = 0
                print("no yellow detect")
                check = Yellow_no
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_yellow += 1
        else:
            if count_yellow < yellow_chance * (-1):
                count_yellow = 0
                print("Complete to Detect Yellow")
                check = Yellow_yes
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_yellow -= 1
        sleep(0.01)
        
        
        #화면 띄우기
        #cv.imshow("Original", src) #원본 화면
        #cv.imshow("Detection of Yellow", res_yellow) #yellow
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break


    cap.release()
    cv2.destroyAllWindows()
'''인식 o :Yellow_yes(51) ///  인식 x :Yellow_no(50)'''

#-----------------------------------------------
############## 검은색 인식(제어보드로부터 Black_detect 수신) ##############

def Black_color_detect(cap, black1, black2, black_chance) -> 6:
    count_blue = 0

    while (True):

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        #HSV H(Hue; 색조), S(Saturation; 채도), V(Value; 명도)
        #powerpoint에서 찾은값에 H는 1/2해줘야함


        mask_blue = cv2.inRange(hsv, black1, black2) # 노랑최소최대값을 이용해서 maskyellow값지정
        
        res_blue = cv2.bitwise_and(src, src, mask=mask_blue) # 노랑색만 추출하기
        switch = 0

        for metrix in res_blue: # row_level
            switch += sum(metrix)

        if sum(switch) == 0:
            if count_blue > black_chance:
                count_blue = 0
                print("no black detect")
                check = Black_no
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_blue += 1
        else:
            if count_blue < black_chance*(-1):
                count_blue = 0
                print("Complete Detect Black!")
                check = Black_yes
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_blue -= 1
        sleep(0.01)
        #화면 띄우기
        #cv.imshow("Original", src) #원본 화면
        #cv.imshow("Detection of blue", res_blue) #원본 화면
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break



    cap.release()
    cv2.destroyAllWindows()
'''인식 o :Blue_yes(61) ///  인식 x :Blue_no(60)'''




#-----------------------------------------------
############## 초록색 인식(제어보드로부터 Green_detect 수신) ##############
def Green_color_detect(cap, green1, green2, green_chance) -> 7:
    count_blue = 0
    black1 = green1
    black2 = green2
    black_chance = green_chance

    while (True):

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        #HSV H(Hue; 색조), S(Saturation; 채도), V(Value; 명도)
        #powerpoint에서 찾은값에 H는 1/2해줘야함


        mask_blue = cv2.inRange(hsv, black1, black2) # 노랑최소최대값을 이용해서 maskyellow값지정
        
        res_blue = cv2.bitwise_and(src, src, mask=mask_blue) # 노랑색만 추출하기
        switch = 0

        for metrix in res_blue: # row_level
            switch += sum(metrix)

        if sum(switch) == 0:
            if count_blue > black_chance:
                count_blue = 0
                print("no green detect")
                check = Green_no
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_blue += 1
        else:
            if count_blue < black_chance*(-1):
                count_blue = 0
                print("Complete Detect Green!")
                check = Green_yes
        #############[ contest ]#################
                return check
        #########################################
            else:
                count_blue -= 1
        sleep(0.01)
        #화면 띄우기
        #cv.imshow("Original", src) #원본 화면
        #cv.imshow("Detection of blue", res_blue) #원본 화면
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break



    cap.release()
    cv2.destroyAllWindows()
'''인식 o :Green_yes(71) ///  인식 x :Green_no(70)'''

    
#-----------------------------------------------
############## 빨간색 인식(제어보드로부터 Red_detect 수신) ##############
# def Red_detect(ser, cap): -> xxxxx
    
#----------------------------------------------- 
#----------------------------------------------- 

def TX_data(ser, one_byte):  # one_byte= 0~255
    #ser.write(chr(int(one_byte)))          #python2.7
    ser.write(serial.to_bytes([one_byte]))  #python3
    
#-----------------------------------------------
def RX_data(ser):

    if ser.inWaiting() > 0:
        result = ser.read(1)
        RX = ord(result)
        return RX
    else:
        return 0

#-----------------------------------------------
def Camera(ser, cap):
    global yellow1
    global yellow2

    while cv2.waitKey(33) < 0:
        _, src = cap.read() #영상파일 읽어드리기
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2)  # 노랑최소최대값을 이용해서 maskyellow값지정
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow)  # 노랑색만 추출하기
        k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dst = cv2.dilate(res_yellow, k)
        imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        cam = cv2.GaussianBlur(imgray, (3, 3), 0)  # 가우시안 블러
        _, cam_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이진화
        contours, _ = cv2.findContours(cam_binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            pass
        else:
            contr = contours[0]
            x, y, w, h = cv2.boundingRect(contr)
            cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 0), 3)

        cv.imshow("Original", src) #원본 화면
        cv.imshow("linetracing ", res_yellow) #원본 화면
        cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()



#-----------------------------------------------
def Receiving(ser, cap):
    global receiving_exit

    global X_255_point
    global Y_255_point
    global X_Size
    global Y_Size
    global Area, Angle
    global Letter_cnt

    # 수신 준비 완료 코드를 제어보드에게 전송함
    TX_data(ser, START)

    receiving_exit = 1
    while True:
        if receiving_exit == 0:
            break
        time.sleep(threading_Time)
        
        while ser.inWaiting() > 0:
            ############## 제어보드로부터 신호 수신 ##############
            result = ser.read(1)
            RX = ord(result) # ord(): 유니코드 정수 반환
            print ("RX=" + str(RX))
            
            ############## 신호에 해당하는 함수 실행 ##############
            # ----- 프로그램 종료 신호 ------
            if RX == 16:
                receiving_exit = 0
                break
        
            else:
                # ----- 방향 인식 신호 ------
                if RX == Arrow_detect:
                    print("---------------- 방향 인식 ------------------")

                    flag = arrow(cap)

                    if(flag == Arrow_no):
                        print("방향 인식되지 않음")
                    if(flag == Arrow_left):
                        print("왼쪽")
                    if(flag == Arrow_right):
                        print("오른쪽")

                # ----- 글자 인식 신호 ------
                elif RX == Alpha_detect:
                    if Letter_cnt == 3:
                        print("---------------- 글자 인식::방위 ------------------")
                    
                    elif Letter_cnt == 2:
                        print("---------------- 글자 인식::1번째 방 ------------------")

                    elif Letter_cnt == 1:
                        print("---------------- 글자 인식::2번째 방 ------------------")
    
                    flag = letterdetect(cap)

                    if(flag == Alpha_no):
                        print("글자 인식되지 않음")
                    if(flag == Alpha_A):
                        print("방 이름: A")
                    if(flag == Alpha_B):
                        print("방 이름: B")
                    if(flag == Alpha_C):
                        print("방 이름: C")
                    if(flag == Alpha_D):
                        print("방 이름: D")
                    if(flag == Alpha_E):
                        print("방위: E(동쪽)")
                    if(flag == Alpha_W):
                        print("방위: W(서쪽)")
                    if(flag == Alpha_S):
                        print("방위: S(남쪽)")
                    if(flag == Alpha_N):
                        print("방위: N(뷱쪽)")
                    
                    

                # ----- 라인트레이싱 신호 ------
                # 확인해야하는 글자 개수
                # : 3개 혹은 2개일 때 -> 들려야하는 미션방이 2개 남은 상태
                # : 1개일 때 -> 들려야하는 미션방이 1개 남은 상태
                # : 0개일 때 -> 들려야하는 미션방이 0개 남은 상태
                elif RX == Line_detect:
                    if Letter_cnt == 3 or Letter_cnt == 2:
                        print("---------------- 1번째 라인 트레이싱 ------------------")
                    if Letter_cnt == 1:
                        print("---------------- 2번째 라인 트레이싱 ------------------")
                    if Letter_cnt == 0:
                        print("---------------- 3번째 라인 트레이싱 ------------------")

                    flag = make_middle_flag(cap, mid_yellow1,mid_yellow2,center_sensitive,mid_sensitive)

                    if(flag == Line_no):
                        print("라인 인식되지 않음")
                    if(flag == Line_mid):
                        print("라인 가운데에 위치")
                    if(flag == Line_left):
                        print("라인이 왼쪽으로 치우침")
                    if(flag == Line_right):
                        print("라인이 오른쪽으로 치우침")
                    
                    TX_data(ser, flag)
                    print(f"TX={flag} ")
                    
                    print("-----angle------")

                    flag = detect_angle(cap, angle_yellow1, angle_yellow2,right_angle,left_angle)
                    
                    if(flag == Line_no):
                        print("라인 인식되지 않음")
                    
                    if(flag == Line_angle_mid):
                        print("라인이 기울어지지 않음")
                    if(flag == Line_angle_left):
                        print("라인이 왼쪽으로 기울어짐")
                    if(flag == Line_angle_right):
                        print("라인이 오른쪽으로 기울어짐")

                    # 미션 수행해야하는 방이 더 이상 없을 때
                    if Letter_cnt < 1:
                        TX_data(ser, flag)
                        print(f"TX={flag} ")

                        flag = detect_ah_eh(cap,mid_yellow1,mid_yellow2,ah_eh_sensitive,ah_eh_rev_sensitive)
                        
                        if(flag == Line_no):
                            print("라인 인식되지 않음")
                        if(flag == Line_threeway_no):
                            print("ㅏ, ㅓ 인식되지 않음")
                        if(flag == Line_threeway_yes):
                            print("ㅏ, ㅓ 인식됨")


                # ----- 시민 인식 신호 ------
                elif RX == BluePerson_detect:
                    # 시민 쪽으로 이동
                    flag = where_is_blue(cap,where_blue1,where_blue2,where_blue_center_sensitive,)
                            
                # ----- 파란색 인식 신호 ------
                elif RX == Blue_detect:
                    flag = Blue_color_detect(cap, blue1, blue2, blue_chance)

                # ----- 노란색 인식 신호 ------ 
                elif RX == Yellow_detect:
                    flag = Yellow_bell_detect(cap,bell_yellow1,bell_yellow2,bell_yellow_chance)

								# ----- 검정색 인식 신호 ------
                elif RX == Black_detect:
                    flag = Black_color_detect(cap, black1, black2, black_chance)

                # # ----- 초록색 인식 신호 ------
                # elif RX == Green_detect:
                #     Green_detect(ser, cap)

                # # ----- 빨간색 인식 신호 ------   
                # elif RX == Red_detect:
                #     Red_detect(ser, cap)
                    
                # -----  신호 x ------    
                else:
                    print("else")
                    continue

            # 실행한 함수로부터 받아온 flag(결과값)를 라즈베리파이보드에게 전송      
            TX_data(ser, flag)
            print(f"TX={flag} ")
            
#-----------------------------------------------
#-----------------------------------------------
    

if __name__ == '__main__':
    
    #-------------------------------------
    
    print ("-------------------------------------")
    print ("---- (2020-1-20)  MINIROBOT Corp. ---")
    print ("-------------------------------------")
   
    os_version = platform.platform()
    print (" ---> OS " + os_version)
    python_version = ".".join(map(str, sys.version_info[:3]))
    print (" ---> Python " + python_version)
    opencv_version = cv2.__version__
    print (" ---> OpenCV  " + opencv_version)
    print ("-------------------------------------")

    #-------------------------------------
    ############## 카메라 오픈 ##############
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    #만약 카메라 안켜지면 위에 카메라 cap 주석처리하고 FPS ~ print 까지 주석 풀어보기

    FPS = 90  # PI CAMERA: 320 x 240 = MAX 90
    
    try:
        cap = cv2.VideoCapture(-1)  # 카메라 켜기  # 카메라 캡쳐 (사진만 가져옴)
    
        cap.set(3, W_View_size)
        cap.set(4, H_View_size)
        cap.set(5, FPS)
    
    except:
        print('cannot load camera!')

    #-------------------------------------
    ############## 제어보드와 라즈베리파이보드 통신 연결 ##############
    BPS =  4800  # 4800,9600,14400, 19200,28800, 57600, 115200

    # local Serial Port : ttyS0
    # USB Serial Port : ttyAMA0
    serial_port = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
    serial_port.flush() # serial cls
    
    print("Ready for camera Thread")
    ############## 카메라 스레드 켜기 ##############
    serial_c = Thread(target=Camera, args=(serial_port, cap,))
    serial_c.daemon = False # 수신을 하는 스레드는 데몬 스레드
    serial_c.start()
    
    #-------------------------------------
    ############## 제어보드로부터 수신받기 시작 ##############
    serial_t = Thread(target=Receiving, args=(serial_port, cap,))
    serial_t.daemon = True # 수신을 하는 스레드는 데몬 스레드
    serial_t.start()
    time.sleep(0.1) 
    
    #-------------------------------------


    #-------------------------------------
    ############## 제어보드에게 송신하는 부분 ##############
    # receiving_exit == 1 -> 리모콘의 전원 버튼 누르면 종료
    while receiving_exit == 1:
        time.sleep(0.01)
        
    #-------------------------------------
    
    cap.release()

    exit(1)
