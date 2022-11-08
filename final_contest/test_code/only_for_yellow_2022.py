import cv2
import cv2 as cv
import numpy as np
from time import sleep 

#cap = cv2.VideoCapture(-1)   #카메라 키는 코드


def Yellow_detect(cap):
    #만약 카메라 안켜지면 위에 카메라 cap 주석처리하고 FPS ~ print 까지 주석 풀어보기
    count_yellow = 0

    ####If You Want to chance Setting -> Please Set these block######
    yellow1 = np.array([16, 80,140])    #min of yellow
    yellow2 = np.array([90, 255,255])   #max of yellow
    yellow_chance = 2 #sensitive (default = 2)
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
