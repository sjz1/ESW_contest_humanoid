import cv2
import cv2 as cv
import numpy as np
from time import sleep 

#cap = cv2.VideoCapture(-1)   #카메라 키는 코드


def Blue_detect(cap):

    count_blue = 0
    ####If You Want to chance Setting -> Please Set these block#####
    ###################################################################3#
    #H:0~179 S:0~255 V:0~255
    blue1 = np.array([91, 159,81])    #min of blue (default : [120-10, 30,30])
    blue2 = np.array([141, 255,255])   #max of blue (default : [120+10, 255,255])
    blue_chance = 2 #sensitive (default = 2)
    ####################################################################


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

