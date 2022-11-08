# *************Seung Jong's Center*****************
import cv2
import cv2 as cv
import numpy as np
from time import sleep




def detect_ah_eh(cap):
    W_View_size = 640
    H_View_size = int(W_View_size / 1.333)

#############################################################################
##############################Threshod Setting###############################
######################### ###0~ 640 기준 250~350##############################
    yellow1 = np.array([16, 80,140])    #min of yellow (default = [16, 80,140])
    yellow2 = np.array([90, 255,255])   #max of yellow (default = [90, 255,255])
    sensitive = 5 #voting count (default = 5)
    rev_sensitive = 20 #ㅓ,ㅏ판단할 때 둔감도
########################################################################
########################################################################
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
    