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


blue1 = np.array([91, 159,81])    #min of blue (default : [120-10, 30,30])
blue2 = np.array([141, 255,255])   #max of blue (default : [120+10, 255,255])
blue_chance = 2 #sensitive (default = 2)

grap_blue_color1 = np.array([91, 159,81])    #min of blue (default : [120-10, 30,30])
grap_blue_color2 = np.array([141, 255,255])   #max of blue (default : [120+10, 255,255])
grap_center_sensitive = 100 #area: center_sensitive x 2 (default = 100)
grap_sensitive = 5 #voting count (default = 5)

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


def Yellow_detect(cap,yellow1,yellow2,yellow_chance):
    
    #만약 카메라 안켜지면 위에 카메라 cap 주석처리하고 FPS ~ print 까지 주석 풀어보기
    count_yellow = 0


    ####################################################################

    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)

    while (True):

        ret, src = cap.read() #영상파일 읽어드리기
        
        src = cv2.resize(src, (W_View_size, H_View_size)) #가져올 파일, ()이미지크기

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
                check = 50
        #############[ contest ]#################
                #return check
        #########################################
            else:
                count_yellow += 1
        else:
            if count_yellow < yellow_chance * (-1):
                count_yellow = 0
                print(switch)
                check = 51
        #############[ contest ]#################
                #return check
        #########################################
            else:
                count_yellow -= 1
        sleep(0.01)
        
        
        #화면 띄우기
        #cv.imshow("Original", src) #원본 화면
        cv.imshow("Detection of Yellow", res_yellow) #yellow
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()
'''인식 o :41 ///  인식 x :40'''

def Blue_detect(cap, blue1, blue2, blue_chance):

    count_blue = 0


    while (True):
        ret, src = cap.read() #영상파일 읽어드리기
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
                check = 40

        #############[ contest ]#################
                #return check
        #########################################
            else:
                count_blue += 1
        else:
            if count_blue < blue_chance*(-1):
                count_blue = 0
                print(switch)
                check = 41

        #############[ contest ]#################
                #return check
        #########################################
            else:
                count_blue -= 1
        sleep(0.01)
        #화면 띄우기
        #cv.imshow("Original", src) #원본 화면
        cv.imshow("Detection of blue", res_blue) #원본 화면
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



    cap.release()
    cv2.destroyAllWindows()
'''인식 o :41 ///  인식 x :40'''

def where_is_blue(cap,where_blue1,where_blue2,where_blue_center_sensitive,):
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
            flag =30
        

        elif flag == 1:
            print("It's Left")
            flag = 32
        
        elif flag == 2:
            print("Robot on Center")
            flag = 31

        else: #3
            print("It's Right")
            flag = 33
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        print(flag)
        ######################contest#######################
        #return flag
        #####################################################

        cv.imshow("Original", src) #원본 화면
        #cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.08)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''인식 x: 30 왼: 32 중앙 31 오른쪽 33'''

############################################################################
########################line trace part ####################################

def make_middle_flag(cap, mid_yellow1,mid_yellow2,center_sensitive,mid_sensitive):
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
            flag =30
        

        elif flag == 1:
            print("It's Left")
            flag = 32
        
        elif flag == 2:
            print("Robot on Center")
            flag = 31

        else: #3
            print("It's Right")
            flag = 33
        
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        print(flag)
        ######################contest#######################
        #return flag
        #####################################################

        cv.imshow("Original", src) #원본 화면
        #cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.08)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()  
''' x: 30 왼: 32 중앙 31 오른쪽 33 '''

def detect_ah_eh(cap,mid_yellow1,mid_yellow2,ah_eh_sensitive,ah_eh_rev_sensitive):
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
            flag =30
        

        elif flag == 1:
            print("I Guess it's ㅓ")
        
        elif flag == 2:
            print("I Guess it's ㅣ")
            flag = 31


        else: #3
            print("I Guess it's ㅏ")
            flag = 33
        
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        print(flag)
        ######################contest#######################
        #return flag
        #####################################################

        cv.imshow("Original", src) #원본 화면
        cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.01)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''x: 30 왼: 32 중앙 31 오른쪽 33 '''

def detect_angle(cap, angle_yellow1, angle_yellow2,right_angle,left_angle):
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
                    print("Warning :: 좌회전 필요")

                elif left_angle < grad_theta < 0:
                    print("Warning :: 우회전 필요")

                else:
                    print("회전 각도 양호")

                sleep(0.3)


                
        cv.imshow("Original", src) #원본파일
        #cv.imshow("yellow_det", hsv) #노랑감지
        #cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", res_yellow) #허프변환라인
        cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP) #확률적허프변환라인
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()
''' 미정'''


#############################################################################
######################## action part ####################################
def grap(cap,grap_blue_color1,grap_blue_color2,grap_center_sensitive,grap_sensitive):
    #yellow라 이름 되어 있지만 blue 입니다
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)
    yellow1 = grap_blue_color1
    yellow2 = grap_blue_color2


    right_flag = 320+grap_center_sensitive
    left_flag = 320-grap_center_sensitive
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


        while (grap_sensitive not in lst_sensitive):
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


                #grap
                if w * h == 200 * 200: 
                    if past == 4: #연속된다면
                        lst_sensitive[4] += 1
                    else: #past = 1,2 연속이 아니였다면
                        lst_sensitive = [0,    0,   0,     0,    0] #초기화시켜주고
                        past = 4 #past를 바꿔주고
                        lst_sensitive[4] += 1

                
                #Center => 2
                if mid_x > left_flag and mid_x < right_flag: 
                    if past == 2: #연속된다면
                        lst_sensitive[2] += 1
                    else: #past = 1,2 연속이 아니였다면
                        lst_sensitive = [0,    0,   0,     0,    0] #초기화시켜주고
                        past = 2 #past를 바꿔주고
                        lst_sensitive[2] += 1
                        
                #Right
                elif mid_x >= right_flag:
                    if past == 3: #연속된다면
                        lst_sensitive[3] += 1
                    else:
                        lst_sensitive = [0,    0,   0,     0,    0] #초기화시켜주고
                        past = 3
                        lst_sensitive[3] += 1
                #Left
                else:
                    if past == 1: #연속된다면
                        lst_sensitive[1] += 1
                    else:
                        lst_sensitive = [0,    0,   0,     0,    0] #초기화시켜주고
                        past = 1
                        lst_sensitive[1] += 1
                print(lst_sensitive)
        flag = lst_sensitive.index(grap_sensitive)
        ################[Can't,  Left,  Center,  Right, grap]#########################
        if flag == 0:
            print("Can't detect blue !!")
            #정현
            #flag =30
        

        elif flag == 1:
            print("It's Left")
            #정현
            #flag = 32
        
        elif flag == 2:
            print("Robot on Center")
            #정현
            #flag = 31

        elif flag == 3:
            print("It's Right")
            #정현
            #flag = 33
        
        else:  #4
            print("Grap the fucking person!!!!")
            #정현
            #flag = 33
        
        

        #in robot
        # x: 30 왼: 32 중앙 31 오른쪽 33
        print(flag)
        ######################contest#######################
        #return flag
        #####################################################

        cv.imshow("Original", src) #원본 화면
        #cv.imshow('Extract Yellow',res_yellow) #추출화면
        sleep(0.08)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''x: 30 왼: 32 중앙 31 오른쪽 33'''


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
# flag = make_middle_flag(cap, mid_yellow1,mid_yellow2,center_sensitive,mid_sensitive) # x: 30 왼: 32 중앙 31 오른쪽 33


# print("파란색 인식 코드 실행")
# check = Blue_detect(cap, blue1, blue2, blue_chance) #인식 o :41 ///  인식 x :40

# print("노란색 인식 코드 실행")
# check = Yellow_detect(cap,yellow1,yellow2,yellow_chance) #인식 o :51 ///  인식 x :50

#print("ㅏ ㅓ ㅡ ㅣ 인식 코드 실행")
#flag = detect_ah_eh(cap,mid_yellow1,mid_yellow2,ah_eh_sensitive,ah_eh_rev_sensitive) # x : // ㅓ : // ㅏ : // ㅣ :  // ㅡ :
#print("회전정렬 코드 실행")
detect_angle(cap, angle_yellow1, angle_yellow2,right_angle,left_angle)