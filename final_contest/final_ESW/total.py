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
Blue_color_detect = 4
Blue_no = 40
Blue_yes = 41

############## 노란색 인식 ##############
Yellow_bell_detect = 5
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

import cv2
import cv2 as cv
import numpy as np
from time import sleep 
import math
#cap = cv2.VideoCapture(-1)   #카메라 키는 코드

###승종 메모###
#아직 grap에 sensitive count_blue 미적용


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

green1= np.array([91, 159,81]) 
green2 = np.array([141, 255,255]) 
green_chance= 2 #sensitive (default = 2)


black1 = np.array([0, 120,110])    #min of blue (default : [120-10, 30,30])
black2 = np.array([50, 136,136])   #max of blue (default : [120+10, 255,255])
black_chance = 2 #sensitive (default = 2)

grap_blue_color1 = np.array([91, 159,81])    #min of blue (default : [120-10, 30,30])
grap_blue_color2 = np.array([141, 255,255])   #max of blue (default : [120+10, 255,255])
grap_sensitive = 5 #voting count (default = 5)
is_near = 180 * 150 #blue is far or near  (default : )

where_blue1 = blue1    #min of blue (default : [120-10, 30,30])
where_blue2   = blue2  #max of blue (default : [120+10, 255,255])
where_blue_center_sensitive = 100 #area: center_sensitive x 2 (default = 100)
where_blue_sensitive = 5 #voting count (default = 5)
########################################################################
########################################################################

#linetrace
###0~ 640 기준 250~350
mid_yellow1 = yellow1    #min of yellow (default = [16, 80,140]) => line trace
mid_yellow2 = yellow2   #max of yellow (default = [90, 255,255]) => line trace
center_sensitive = 100 #area: center_sensitive x 2 (default = 100)
mid_sensitive = 5 #voting count (default = 5)

ah_eh_sensitive = 5 #voting count (default = 5)
ah_eh_rev_sensitive = 20 #ㅓ,ㅏ판단할 때 둔감도


angle_yellow1 = np.array([16, 80,140])
angle_yellow2= np.array([90, 255,255])
right_angle = 1 # (정상 최대 오른각도   default = 1)
left_angle = -1  #right_angle * (-1) 권장

########################################################################
########################################################################


############################################################################
################################ Color Part ################################


def Yellow_bell_detect(src,bell_yellow1,bell_yellow2,bell_yellow_chance) -> 5:
    
    #만약 카메라 안켜지면 위에 카메라 cap 주석처리하고 FPS ~ print 까지 주석 풀어보기
    count_yellow = 0

    ####################################################################
    yellow1=bell_yellow1
    yellow2=bell_yellow2
    yellow_chance = bell_yellow_chance

    while (True):

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
        #sleep(0.01)
        
        
        #화면 띄우기
        #cv.imshow("Original", src) #원본 화면
        #cv.imshow("Detection of Yellow", res_yellow) #yellow
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break


    cap.release()
    cv2.destroyAllWindows()
'''인식 o :Yellow_yes(51) ///  인식 x :Yellow_no(50)'''

def Blue_color_detect(cap, blue1, blue2, blue_chance) -> 4:
    count_blue = 0

    while (True):
        _, src = cap.read() #영상파일 읽어드리기
        src = cv2.resize(src, (640, int(640 / 1.333))) #가져올 파일, ()이미지크기

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
        src = cv2.resize(src, (W_View_size, H_View_size)) #가져올 파일, ()이미지크기

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

############################################################################
########################line trace part ####################################

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
        src = cv2.resize(src, (W_View_size, H_View_size)) #가져올 파일, ()이미지크기

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
                print(lst_sensitive)
        flag = lst_sensitive.index(sensitive)
        ################[Can't,  Left,  Center,  Right]#########################
        if flag == 0:
            print("Can't detect Yellow !!")
            flag =Line_no
        

        elif flag == 1:
            print("It's Left")
            flag = Line_left
        
        elif flag == 2:
            print("Robot on Center")
            flag = Line_mid

        else: #3
            print("It's Right")
            flag = Line_right
        
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        print(flag)
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
        src = cv2.resize(src, (W_View_size, H_View_size)) #가져올 파일, ()이미지크기

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
            print(lst_sensitive)
        flag = lst_sensitive.index(sensitive)
        ################[Can't,  Left,  Center,  Right]#########################
        sleep(1)
        if flag == 0:
            print("Can't detect Yellow !!")
            flag =Line_no
        

        elif flag == 1:
            print("I Guess it's ㅓ")
            flag = Line_threeway_yes
        
        elif flag == 2:
            print("I Guess it's ㅣ")
            flag = Line_threeway_no


        else: #3
            print("I Guess it's ㅏ")
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

def detect_angle(cap, angle_yellow1, angle_yellow2,right_angle,left_angle) -> 3:
    yellow1,yellow2 = angle_yellow1, angle_yellow2
    while (True):
        _ , src = cap.read() #영상파일 읽어드리기
        src = cv2.resize(src, (640, 360)) #가져올 파일, ()이미지크기
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2) # 노랑최소최대값을 이용해서 maskyellow값지정      
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow) # 노랑색만 추출하기     
        srcs = res_yellow    #imgs에 추출한 노랑색 저장
        imgray = cv2.cvtColor(srcs, cv2.COLOR_BGR2GRAY)
        dst = cv2.Canny(imgray, 50, 200, None, 3) #canny처리하기
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
                cv.line(cdst, pt1, pt2, (0, 0, 255), 3, cv.LINE_AA) #라인그리기
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


                
        #cv.imshow("Original", src) #원본파일
        #cv.imshow("yellow_det", hsv) #노랑감지
        #cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", res_yellow) #허프변환라인
        #cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP) #확률적허프변환라인
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break


    cap.release()
    cv2.destroyAllWindows()
''' 똑바름 : Line_angle_mid(36) / 좌회전 필요 : Line_angle_left(37) / 우회전 필요 : Line_angle_right(38) '''

#############################################################################
######################## action part ####################################
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
        src = cv2.resize(src, (W_View_size, H_View_size)) #가져올 파일, ()이미지크기

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



#############################[add part ] ##############################
def detect_angle_adding_undetect(cap, angle_yellow1, angle_yellow2,right_angle,left_angle) -> 3:
    yellow1,yellow2 = angle_yellow1, angle_yellow2
    while (True):
        _ , src = cap.read() #영상파일 읽어드리기
        src = cv2.resize(src, (640, 360)) #가져올 파일, ()이미지크기
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask_yellow = cv2.inRange(hsv, yellow1, yellow2) # 노랑최소최대값을 이용해서 maskyellow값지정      
        res_yellow = cv2.bitwise_and(src, src, mask=mask_yellow) # 노랑색만 추출하기     
        srcs = res_yellow    #imgs에 추출한 노랑색 저장
        imgray = cv2.cvtColor(srcs, cv2.COLOR_BGR2GRAY)
        dst = cv2.Canny(imgray, 50, 200, None, 3) #canny처리하기
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
                cv.line(cdst, pt1, pt2, (0, 0, 255), 3, cv.LINE_AA) #라인그리기
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
        #cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", res_yellow) #허프변환라인
        #cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP) #확률적허프변환라인
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break


    cap.release()
    cv2.destroyAllWindows()
''' 똑바름 : Line_angle_mid(36) / 좌회전 필요 : Line_angle_left(37) / 우회전 필요 : Line_angle_right(38) / Line_no = 30'''

T_sensitive = 5
T_order = 30 #(양 끝점의 오차 거리)
length_T = 600 # T자의 최소 가로 길이 (default = 600)
def detect_T(cap, T_yellow1,T_yellow2,center_sensitive,T_sensitive,T_order,length_T) -> 3:
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    right_flag = 320+center_sensitive
    left_flag = 320-center_sensitive
    ################[Can't,  X,     T]#########################
    lst_sensitive = [0,      0,     0]
    past = 0
    sensitive = T_sensitive

    while(True):
        _, src = cap.read() #영상파일 읽어드리기
        src = cv2.resize(src, (W_View_size, H_View_size)) #가져올 파일, ()이미지크기

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        yellow1 = T_yellow1
        yellow2 = T_yellow2
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
                    lst_sensitive = [0,   0,     0]#초기화시켜주고
                    past = 0 #past를 바꿔주고
                    lst_sensitive[0] += 1
            else:
                contr = contours[0]
                x, y, w, h = cv2.boundingRect(contr)  # 최소한의 사각형 그려주는 함수
                cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 0), 3)
                
                #T => 2
                if w > length_T or x > 640-T_order or x < T_order :
                    if past == 2: #연속된다면
                        lst_sensitive[2] += 1
                    else: #past = 1,2 연속이 아니였다면
                        lst_sensitive = [0, 0  ,0]#초기화시켜주고
                        past = 2 #past를 바꿔주고
                        lst_sensitive[2] += 1
                        
                else:# x => 1
                    if past == 3: #연속된다면
                        lst_sensitive[1] += 1
                    else:
                        lst_sensitive = [0,  0,  0]#초기화시켜주고
                        past = 3
                        lst_sensitive[1] += 1

        flag = lst_sensitive.index(sensitive)
        ################[Can't, X,  T]#########################
        if flag == 0:
            print("Can't detect Yellow !!")
            flag =Line_no
        

        elif flag == 1:
            print("No T Detect")
            #flag = Line_left
        
        else: #2
            print("There is T")
            #flag = Line_right

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        print(flag)
        ######################contest#######################
        return flag
        #####################################################

''' x: Line_no(30) /  T_nondetect / T_detect '''


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
    print("Get ready to camera!")

except:
    print('cannot load camera!')

while cv2.waitKey(33) < 0:
    _, src = cap.read() #영상파일 읽어드리기
    #cv.imshow("Original", src) #원본 화면
    #print("중앙정렬 코드 실행")
    #flag = make_middle_flag(cap, mid_yellow1,mid_yellow2,center_sensitive,mid_sensitive) # x: 30 왼: 32 중앙 31 오른쪽 33
    # print("파란색 인식 코드 실행")
    # check = Blue_detect(cap, blue1, blue2, blue_chance) #인식 o :41 ///  인식 x :40

    print("노란색 인식 코드 실행")
    #check = Yellow_bell_detect(src,yellow1,yellow2,yellow_chance) #인식 o :51 ///  인식 x :50

    middle_using_hough(cap, mid_yellow1,mid_yellow2,center_sensitive,mid_sensitive)
    #print("ㅏ ㅓ ㅡ ㅣ 인식 코드 실행")
    #flag = detect_ah_eh(cap,mid_yellow1,mid_yellow2,ah_eh_sensitive,ah_eh_rev_sensitive) # x : // ㅓ : // ㅏ : // ㅣ :  // ㅡ :
    #print("회전정렬 코드 실행")
    #detect_angle(cap, angle_yellow1, angle_yellow2,right_angle,left_angle)

    #print("Grap 코드 실행")
    #grap(src,grap_blue_color1,grap_blue_color2,is_near,grap_sensitive)
    
    #cv.imshow('Extract Yellow',res_yellow) #추출화면
    sleep(0.08)

cap.release()
cv2.destroyAllWindows()