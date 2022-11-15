'******** 송수신 데이터 ********

CONST LETGO = 0

CONST Arrow_detect = 1
CONST Arrow_no = 10
CONST Arrow_left = 11
CONST Arrow_right = 12

CONST Alpha_detect = 2
CONST Alpha_no= 20
CONST Alpha_E = 21
CONST Alpha_W = 22
CONST Alpha_S = 23
CONST Alpha_N = 24
CONST Alpha_A = 25
CONST Alpha_C = 26
CONST Alpha_B = 27
CONST Alpha_D = 28

CONST Line_detect = 3
CONST Line_no = 30
CONST Line_mid = 31
CONST Line_left = 32
CONST Line_right = 33
CONST Line_threeway_no = 34
CONST Line_threeway_yes = 35
CONST Line_angle_mid = 36
CONST Line_angle_left = 37
CONST Line_angle_right = 38

CONST Blue_detect = 4
CONST Blue_no = 40
CONST Blue_yes = 41

CONST Yellow_detect = 5
CONST Yellow_no = 50
CONST Yellow_yes = 51

CONST Black_detect = 6
CONST Black_no = 60
CONST Black_yes = 61

CONST Green_detect = 7
CONST Green_no = 70
CONST Green_yes = 71

CONST Red_detect = 8
CONST Red_no = 80
CONST Red_yes = 81

CONST BluePerson_detect = 9
CONST BluePerson_detect_no = 90
CONST BluePerson_detect_mid = 91
CONST BluePerson_detect_left = 92
CONST BluePerson_detect_right = 93
CONST BluePerson_detect_grap = 94

'******** 기타 데이터 ********

CONST TRUE = 1
CONST FALSE = 0

DIM S AS BYTE ' 데이터 수신
DIM DIRECTION AS BYTE ' 방향 저장
DIM ROOM AS BYTE ' 방이름 저장
DIM DANGEROUS_ROOM AS BYTE ' 위험지역 미션방 이름 저장
DIM LETTER_CNT AS BYTE ' 남은 문자(방위, 방이름) 개수
DIM UPDOWN AS BYTE ' 고개 상하 동작 각고

DIM IS_PERSON AS BYTE ' 시민 인식 여부

IS_PERSON = FALSE

LETTER_CNT = 3

'******** 2족 보행로봇 초기 영점 프로그램 ********

DIM A AS BYTE
DIM A_old AS BYTE
DIM B AS BYTE
DIM I AS BYTE
DIM MODE AS BYTE
DIM 넘어진확인 AS BYTE
DIM 기울기확인횟수 AS BYTE
DIM 적외선거리값  AS BYTE
DIM 보행순서 AS BYTE
DIM 보행횟수 AS BYTE
DIM 보행COUNT AS BYTE
DIM 반전체크 AS BYTE
DIM 모터ONOFF AS BYTE
DIM 자이로ONOFF AS BYTE
DIM 보행속도 AS BYTE
DIM 좌우속도 AS BYTE

DIM NO_0 AS BYTE
DIM NO_1 AS BYTE
DIM NO_2 AS BYTE
DIM NO_3 AS BYTE
DIM NO_4 AS BYTE
DIM NUM AS BYTE

DIM S11 AS BYTE
DIM S16 AS BYTE

DIM BUTTON_NO AS INTEGER
DIM SOUND_BUSY AS BYTE
DIM TEMP_INTEGER AS INTEGER

'**** 기울기센서포트 설정 ****

CONST 앞뒤기울기AD포트 = 0
CONST 좌우기울기AD포트 = 1
CONST 적외선AD포트  = 4

CONST 기울기확인시간 = 20  'ms

CONST min = 61	'뒤로넘어졌을때
CONST max = 107	'앞으로넘어졌을때
CONST COUNT_MAX = 3

CONST 머리이동속도 = 10

'************************************************

PTP SETON 				'단위그룹별 점대점동작 설정
PTP ALLON				'전체모터 점대점 동작 설정

DIR G6A,1,0,0,1,0,0		'모터0~5번
DIR G6D,0,1,1,0,1,1		'모터18~23번
DIR G6B,1,1,1,1,1,1		'모터6~11번
DIR G6C,0,0,0,0,1,0		'모터12~17번

'************************************************

OUT 52,0	'머리 LED 켜기

'***** 초기선언 '************************************************

보행순서 = 0
반전체크 = 0
기울기확인횟수 = 0
보행횟수 = 1
모터ONOFF = 0

'****초기위치 피드백*****************************

TEMPO 230
'MUSIC "cdefg"

SPEED 5
GOSUB MOTOR_ON

S11 = MOTORIN(11)
S16 = MOTORIN(16)

SERVO 11, 100
SERVO 16, S16

SERVO 16, 100

GOSUB 전원초기자세
GOSUB 기본자세

GOSUB 자이로INIT
GOSUB 자이로MID
GOSUB 자이로ON

' PRINT "VOLUME 200 !"
' PRINT "SOUND 12 !" '안녕하세요

GOSUB All_motor_mode3

GOTO MAIN_0	'시리얼 수신 루틴으로 가기

'*************************************************************************
'*************************************************************************
'************************** 제어보드 알고리즘 부분 *****************************
'*************************************************************************
'*************************************************************************

MAIN_0:
    ERX 4800,A,MAIN_0 ' 로봇 연결 될 때까지 대기

    IF A = LETGO THEN ' 라즈베리파이로부터 0 수신 시, 코드 시작
        GOTO MAIN
    ELSE
        GOTO MAIN_0
    ENDIF

MAIN:
    GOSUB 앞뒤기울기측정
    GOSUB 좌우기울기측정
    GOSUB 적외선거리센서확인

    GOTO 라인트레이싱

라인트레이싱:
	UPDOWN = 20
	GOSUB 고개동작
	
    DELAY 1000

    ETX 4800,Line_detect

    GOTO 라인트레이싱_시작

라인트레이싱_시작:
    ERX 4800,S,라인트레이싱_시작

    ' 라인 인식되지 않았을 때
    IF S = Line_no THEN
    	GOSUB 신호버리기

        IF LETTER_CNT = 0 THEN ' 세번째 라인트레이싱
            GOSUB 신호버리기

            GOSUB 만세
            WAIT
            GOSUB 위험미션방소리내기
            WAIT
            GOSUB 기본자세

            ETX 4800, 16
            END

        ENDIF
		
        IF LETTER_CNT = 3 THEN ' 방위 인식
            UPDOWN = 70
        ELSE ' 방이름 인식
            UPDOWN = 100
        ENDIF				

        GOSUB 고개동작
        GOTO 글자인식

        ' 라인 인식되었을 때
    ELSE
        IF LETTER_CNT = 3 OR LETTER_CNT = 2 THEN
            ' 라인이 중앙에 있는 경우 -> 4걸음 전진
            IF S = Line_mid THEN
                IF LETTER_CNT = 3 THEN
                    GOSUB 정확전진
                ELSE
                    보행횟수 = 4
                    GOSUB 전진
                ENDIF
	
	            ' 라인이 왼쪽으로 치우친 경우 -> 4걸음 좌측 대각선 이동
	        ELSEIF S = Line_left THEN
	        	FOR I = 1 TO 2
	             GOSUB 왼쪽횡으로이동 
	             NEXT I
	             WAIT
	             
	             보행횟수 = 1
	             GOSUB 전진
	
	            ' 라인이 우측에 있는 경우 -> 4걸음 우측 대각선 이동
	        ELSEIF S = Line_right THEN
	        	FOR I = 1 TO 2
	             GOSUB 오른쪽횡으로이동
	             NEXT I
	             WAIT
	             
	             보행횟수 = 1
	             GOSUB 전진
	
	        ENDIF
	
	        GOSUB 앵글조정

		ELSEIF LETTER_CNT = 1 THEN
			' 라인이 중앙에 있는 경우 -> 4걸음 전진
	        IF S = Line_mid THEN
                IF DIRECTION = Arrow_left THEN
                    보행횟수 = 4
                    GOSUB 전진
                    
                    GOSUB 오른쪽횡으로이동
                    
                ELSEIF DIRECTION = Arrow_right THEN
                    보행횟수 = 4
                GOSUB 전진 
                WAIT
            
                GOSUB 왼쪽횡으로이동
            
                ENDIF
            
	        ' 라인이 왼쪽으로 치우친 경우 -> 4걸음 좌측 대각선 이동
	        ELSEIF S = Line_left THEN
	             GOSUB 왼쪽횡으로이동
	             WAIT
	             DELAY 500
	             보행횟수 = 1
	             GOSUB 전진
	
	        ' 라인이 우측에 있는 경우 -> 4걸음 우측 대각선 이동
	        ELSEIF S = Line_right THEN
	            GOSUB 오른쪽횡으로이동 
				WAIT
				DELAY 500
				보행횟수 = 1
				GOSUB 전진
	        ENDIF
	
	        GOSUB 앵글조정

        ELSEIF LETTER_CNT = 0 THEN
			' 라인이 중앙에 있는 경우 -> 4걸음 전진
	        IF S = Line_mid THEN
	            GOSUB 정확전진
	
	            ' 라인이 왼쪽으로 치우친 경우 -> 4걸음 좌측 대각선 이동
	        ELSEIF S = Line_left THEN
	             GOSUB 왼쪽횡으로이동
	
	            ' 라인이 우측에 있는 경우 -> 4걸음 우측 대각선 이동
	        ELSEIF S = Line_right THEN
	             GOSUB 오른쪽횡으로이동 
	
	        ENDIF
	
	        GOSUB 앵글조정
            GOSUB 세갈래길인식

        ENDIF

        GOTO MAIN
    ENDIF

신호버리기:
    ERX 4800,S,신호버리기

    RETURN

세갈래길인식:
    ERX 4800,S,세갈래길인식

    ' 세갈래길이 인식되었을 때 (인식되지 않으면 무시함)
    IF S = Line_threeway_yes THEN
        IF LETTER_CNT = 1 THEN ' 두번째 라인트레이싱
            보행횟수 = 4
            GOSUB 전진

        ELSEIF LETTER_CNT = 0 THEN ' 세번째 라인트레이싱
            IF DIRECTION = Arrow_left THEN
                GOSUB 좌회전90도

            ELSEIF DIRECTION = Arrow_right THEN
                GOSUB 우회전90도

            ENDIF
        ENDIF
    ENDIF

    RETURN

    ' 나중에 앵글조정 부분 따로 빼서 앵글 맞출 때까지 무한반복 시켜야할듯
앵글조정:
    ERX 4800,S,앵글조정

    ' 선이 왼쪽으로 기울었을 때
    IF S = Line_angle_left THEN
        GOSUB 좌회전10도

    ' 선이 오른쪽으로 기울었을 때
    ELSEIF S = Line_angle_right THEN
        GOSUB 우회전10도

    ' 선이 기울지 않았을 때에는 아무런 행동도 하지 않음
    ENDIF

    RETURN

글자인식:
    ETX  4800,Alpha_detect

    GOTO 글자인식_시작

글자인식_시작:
    ERX 4800,S,글자인식_시작

    ' 글자 인식하지 못한 경우
    IF S = Alpha_no THEN
        ' 방위 인식할 때
		IF LETTER_CNT = 3 THEN
            UPDOWN = UPDOWN + 20
            GOSUB 고개동작

        ' 방이름 확인할 때
        ELSE
            보행횟수 = 1
            GOSUB 전진
            
        ENDIF

        GOTO 글자인식

    ' 방위를 인식한 경우
    ELSEIF S < Alpha_A THEN
        LETTER_CNT = LETTER_CNT - 1

        ' E -> 오른팔 앞으로 들기 + "동쪽 동쪽" 소리내기
        IF S = Alpha_E THEN
            GOSUB 오른팔앞으로들기
            WAIT
            GOSUB 동쪽동쪽소리내기
            WAIT
            GOSUB 팔제자리

        ' W -> 왼팔 앞으로 들기 + "서쪽 서쪽" 소리내기
        ELSEIF S = Alpha_W THEN
            GOSUB 왼팔앞으로들기
            WAIT
            GOSUB 서쪽서쪽소리내기
            WAIT
            GOSUB 팔제자리

        ' S -> 양손 뒤로 나란히 들기 + "남쪽 남쪽" 소리내기
        ELSEIF S = Alpha_S THEN
            GOSUB 양손뒤로나란히들기
            WAIT
            GOSUB 남쪽남쪽소리내기
            WAIT
            GOSUB 팔제자리

        ' N -> 양손 앞으로 나란히 들기 + "북쪽 북쪽" 소리내기
        ELSEIF S = Alpha_N THEN
            GOSUB 양손앞으로나란히들기
            WAIT
            GOSUB 북쪽북쪽소리내기
            WAIT
            GOSUB 팔제자리

        ENDIF
        
        UPDOWN = UPDOWN + 20
        GOSUB 고개동작

        GOTO 방향인식
    
    ' 방이름을 인식한 경우
    ELSE
        LETTER_CNT = LETTER_CNT - 1

        ROOM = S ' 방이름 저장
        GOTO 미션

    ENDIF

방향인식:
    ETX  4800,Arrow_detect

    GOTO 방향인식_시작

방향인식_시작:
    ERX 4800,S,방향인식_시작

    ' 방향 인식안됨 ->  고개 살짝 들기 + 다시 방향인식
    IF S = Arrow_no THEN
	    UPDOWN = UPDOWN + 10
        GOSUB 고개동작
        GOTO 방향인식

    ' 왼쪽 화살표 -> 좌회전
    ELSEIF S = Arrow_left THEN
        DIRECTION = S
        GOSUB 좌회전90도

    ELSEIF S = Arrow_right THEN
        DIRECTION = S
        GOSUB 우회전90도

    ENDIF
    
    GOTO MAIN

미션:
    ' 화살표 방향이 왼쪽이였을때 -> 왼쪽횡무빙 + 직진 + 미션 + 우회전 + 직진 + 오른쪽횡무빙 + 직진 
    IF DIRECTION = Arrow_left THEN
        FOR I = 1 TO 2
        GOSUB 왼쪽횡으로이동
        NEXT I

        DELAY 500
        
    ' 화살표 방향이 오른쪽이였을때 -> 오른쪽횡무빙 + 직진 + 미션 + 좌회전 + 직진 + 왼쪽횡무빙 + 직진 
    ELSEIF DIRECTION = Arrow_right THEN
        FOR I = 1 TO 2
        GOSUB 오른쪽횡으로이동
        NEXT I

        DELAY 500

    ENDIF

    UPDOWN = 65
    GOSUB 고개동작

    GOTO 미션확인

미션확인:
    ETX 4800, Black_detect

    GOTO 미션확인_시작

미션확인_시작:
    ERX 4800, S, 미션확인_시작

    ' 검은색 인식되지 않음 -> 계단지역 미션
    IF S = Black_no THEN
       ' GOTO 계단지역

    ' 검은색 인식됨 -> 위험지역::시민구출 미션
    ELSE
        DANGEROUS_ROOM = ROOM ' 위험지역 방 이름 저장
        DELAY 2000
        GOTO 시민찾기
    
    ENDIF

' 계단지역:

시민찾기:
    DELAY 2000
    ETX 4800, BluePerson_detect
    DELAY 2000
    ' 시민을 못찾은 경우 -> 고개 각도 조절 및 횡무빙을 통해 시민찾기
    IF IS_PERSON = FALSE THEN
        
        GOTO 시민찾기_시작
    ' 시민을 찾은 경우 -> 시민에게 다가가기
    ELSE
        
        GOTO 시민에게다가가기
    ENDIF

시민찾기_시작:
    ERX 4800, S, 시민찾기_시작
    DELAY 2000
    ' 시민이 보이지 않을 때 -> 고개 각도 조절 및 횡무빙
    IF S = BluePerson_detect_no THEN
        ' 고개를 최대한 내렸는데도 시민이 보이지 않을 때 -> 횡무빙
        IF UPDOWN < 25 THEN
            ' 화살표 방향이 왼쪽이였을때 -> 왼쪽횡무빙
            IF DIRECTION = Arrow_left THEN
                FOR I = 1 TO 2
                GOSUB 왼쪽옆으로70연속
                NEXT I

                DELAY 2000
                
            ' 화살표 방향이 오른쪽이였을때 -> 오른쪽횡무빙
            ELSEIF DIRECTION = Arrow_right THEN
                FOR I = 1 TO 2
                GOSUB 오른쪽옆으로70연속
                NEXT I

                DELAY 2000

            ENDIF
			WAIT
            UPDOWN = 65
            GOSUB 고개동작
            DELAY 2000

        ' 고개 내려서 시민 다시 찾기
        ELSE
            UPDOWN = UPDOWN -20
            GOSUB 고개동작
            DELAY 2000
        ENDIF

        GOTO 시민찾기
    
    ' 시민 찾았을 때 -> 위험지역 소리내기 + 시민에게 다가가기
    ELSE
        IS_PERSON = TRUE
        GOSUB 위험지역소리내기
        DELAY 2000
        GOTO 시민찾기
    
    ENDIF

시민에게다가가기:
    DELAY 2000
    ERX 4800, S, 시민에게다가가기

    ' 시민이 보이지 않을 때 -> 고개 각도 조절 통해 시민 찾기 또는 시민 잡기
    IF S = BluePerson_detect_no THEN
        IF UPDOWN < 45 THEN
       		WAIT
        	SERVO 16, 100
        	WAIT
            GOSUB 시민잡기
            WAIT
            
            DELAY 2000
            
            
            IF DIRECTION = Arrow_left THEN
                FOR I = 1 TO 3
            	GOSUB 집고오른쪽턴45
            	DELAY 2000
            	NEXT I
            
        ' 화살표 방향이 오른쪽이였빙
        	ELSEIF DIRECTION = Arrow_right THEN
        		FOR I = 1 TO 5
           		GOSUB 집고왼쪽턴20
           	    DELAY 2000
           	    NEXT I
            
       	    ENDIF
            
        
            WAIT
            
            DELAY 2000
            
            GOSUB 시민놓기
            WAIT
            
            GOSUB 자이로INIT
            WAIT
			GOSUB 자이로MID
			WAIT
			GOSUB 자이로ON
			WAIT
			GOSUB 기본자세
			WAIT
			DELAY 500
			            
			
			
			GOSUB 정확전진
			
			DELAY 500
			
			GOSUB 정확전진
			
			DELAY 500
			
			GOSUB 정확전진
			
			DELAY 500
			
			GOSUB 정확전진
			
			DELAY 500
			
			GOSUB 정확전진
			
			DELAY 500
			
		    GOSUB 정확전진
			
			DELAY 500
			
			
			
			
			
			DELAY 2000
			
			WAIT
			
			SERVO 16,20
			
			WAIT
			
			DELAY 100
			
			GOTO 라인트레이싱복귀
            
        ELSE
            UPDOWN = UPDOWN - 20
            GOSUB 고개동작
            DELAY 2000

        ENDIF
    
    ' 시민이 보일 때 -> 시민 트레이싱
    ELSE
        IF S = BluePerson_detect_mid THEN
            GOSUB 정확전진

        ELSEIF S = BluePerson_detect_left THEN
             GOSUB 왼쪽횡으로이동

        ELSEIF S = BluePerson_detect_right THEN
             GOSUB 오른쪽횡으로이동

        ENDIF

    ENDIF
    DELAY 2000
    GOTO 시민찾기

라인트레이싱복귀:
    ETX 4800, Yellow_detect

    GOTO 라인트레이싱복귀_시작

라인트레이싱복귀_시작:
    ERX 4800, S, 라인트레이싱복귀_시작

    ' 노란색이 인식되지 않으면 -> 횡무빙
    IF S = Yellow_no THEN
        ' 화살표 방향이 왼쪽이였을때 -> 오른쪽횡무빙
        IF DIRECTION = Arrow_left THEN
            GOSUB 오른쪽옆으로70연속
            
        ' 화살표 방향이 오른쪽이였을때 -> 왼쪽횡무빙
        ELSEIF DIRECTION = Arrow_right THEN
            GOSUB 왼쪽옆으로70연속
            
        ENDIF

        GOTO 라인트레이싱복귀

    ' 노란색이 인식되면 -> 라인트레이싱 시작
    ELSE
        GOTO MAIN

    ENDIF

위험미션방소리내기:
    ' 위험미션방이 A일 때
    IF DANGEROUS_ROOM = Alpha_A THEN
	    GOSUB A소리내기

    ' 위험미션방이 B일 때
    ELSEIF DANGEROUS_ROOM = Alpha_B THEN
	    GOSUB B소리내기

    ' 위험미션방이 C일 때
    ELSEIF DANGEROUS_ROOM = Alpha_C THEN
	    GOSUB C소리내기

    ' 위험미션방이 D일 때
    ELSEIF DANGEROUS_ROOM = Alpha_D THEN
	    GOSUB D소리내기

    ENDIF

    RETURN  


'*************************************************************************
'*************************************************************************
'*************************** 사용자 정의 label ******************************
'*************************************************************************
집고왼쪽턴45:

    GOSUB Leg_motor_mode2
    SPEED 8
    MOVE G6A,95,  106, 145,  55, 105, 100
    MOVE G6D,95,  46, 145,  115, 105, 100
    WAIT
    

    SPEED 10
    MOVE G6A,93,  106, 145,  55, 105, 100
    MOVE G6D,93,  46, 145,  115, 105, 100
    WAIT

    SPEED 8
    MOVE G6A,100,  76, 145,  85, 100
    MOVE G6D,100,  76, 145,  85, 100
    WAIT
    GOSUB Leg_motor_mode1
    WAIT
    RETURN
'*************************************************************************

정확전진:
	
    보행COUNT = 0
    보행속도 = 8
    좌우속도 = 3
    넘어진확인 = 0

        SPEED 4

        MOVE G6A, 88,  74, 144,  95, 110
        MOVE G6D,108,  76, 146,  93,  96
        MOVE G6B,100
        MOVE G6C,100
        WAIT

        SPEED 8

        MOVE G6A, 90, 90, 120, 105, 110,100
        MOVE G6D,110,  76, 147,  93,  96,100
        MOVE G6B,90
        MOVE G6C,110
        WAIT

    SPEED 보행속도

    MOVE G6A, 86,  56, 145, 115, 110
    MOVE G6D,108,  76, 147,  93,  96
    WAIT


    SPEED 좌우속도
   

    MOVE G6A,110,  76, 147, 93,  96
    MOVE G6D,86, 100, 145,  69, 110
    WAIT


    SPEED 보행속도

    GOSUB 앞뒤기울기측정
	  WAIT


    MOVE G6A,110,  76, 147,  93, 96,100
    MOVE G6D,90, 90, 120, 105, 110,100
    MOVE G6B,110
    MOVE G6C,90
    WAIT

    

    SPEED 보행속도

    MOVE G6D, 86,  56, 145, 115, 110
    MOVE G6A,108,  76, 147,  93,  96
    WAIT

    SPEED 좌우속도
    MOVE G6D,110,  76, 147, 93,  96
    MOVE G6A,86, 100, 145,  69, 110
    WAIT

    SPEED 보행속도

    GOSUB 앞뒤기울기측정
 
	WAIT

    MOVE G6A,90, 90, 120, 105, 110,100
    MOVE G6D,110,  76, 146,  93,  96,100
    MOVE G6B, 90
    MOVE G6C,110
    WAIT
	SPEED 4
	
	MOVE G6A,100,  76, 145,  93, 100, 100
    MOVE G6D,100,  76, 145,  93, 100, 100
    MOVE G6B,100,  30,  80,
    MOVE G6C,100,  30,  80
    WAIT
	
	RETURN
	'*********************************
전진:
    GOSUB All_motor_mode3
    보행COUNT = 0
    SPEED 7
    HIGHSPEED SETON

    IF 보행순서 = 0 THEN
        보행순서 = 1
        MOVE G6A,95,  76, 147,  93, 101
        MOVE G6D,101,  76, 147,  93, 98
        MOVE G6B,100
        MOVE G6C,100
        WAIT

        GOTO 전진1
    ELSE
        보행순서 = 0
        MOVE G6D,95,  76, 147,  93, 101
        MOVE G6A,101,  76, 147,  93, 98
        MOVE G6B,100
        MOVE G6C,100
        WAIT

        GOTO 전진4
    ENDIF

    '**********************

전진1:
    MOVE G6A,95,  90, 125, 100, 104
    MOVE G6D,104,  77, 147,  93,  102
    MOVE G6B, 85
    MOVE G6C,115
    WAIT

전진2:

    MOVE G6A,103,   73, 140, 103,  100
    MOVE G6D, 95,  85, 147,  85, 102
    WAIT

    GOSUB 앞뒤기울기측정
    IF 넘어진확인 = 1 THEN
        넘어진확인 = 0

        RETURN
    ENDIF

    보행COUNT = 보행COUNT + 1
    IF 보행COUNT > 보행횟수 THEN  GOTO 전진2_stop

	GOTO 전진4

    'ERX 4800,A, 전진4
    'IF A <> A_old THEN
전진2_stop:
        MOVE G6D,95,  90, 125, 95, 104
        MOVE G6A,104,  76, 145,  91,  102
        MOVE G6C, 100
        MOVE G6B,100
        WAIT
        HIGHSPEED SETOFF
        SPEED 15
        GOSUB 안정화자세
        SPEED 5
        GOSUB 기본자세2

        'DELAY 400
        RETURN
    'ENDIF

    '*********************************

전진4:
    MOVE G6D,95,  95, 120, 100, 104
    MOVE G6A,104,  77, 147,  93,  102
    MOVE G6C, 85
    MOVE G6B,115
    WAIT

전진5:
    MOVE G6D,103,    73, 140, 103,  100
    MOVE G6A, 95,  85, 147,  85, 102
    WAIT

    GOSUB 앞뒤기울기측정
    IF 넘어진확인 = 1 THEN
        넘어진확인 = 0
        RETURN
    ENDIF

    보행COUNT = 보행COUNT + 1
    IF 보행COUNT > 보행횟수 THEN  GOTO 전진5_stop

	GOTO 전진1

    'ERX 4800,A, 전진1
    'IF A <> A_old THEN
전진5_stop:
        MOVE G6A,95,  90, 125, 95, 104
        MOVE G6D,104,  76, 145,  91,  102
        MOVE G6B, 100
        MOVE G6C,100
        WAIT
        HIGHSPEED SETOFF
        SPEED 15
        GOSUB 안정화자세
        SPEED 5
        GOSUB 기본자세2

        'DELAY 400
        RETURN
    'ENDIF

    '*************************************

    '*********************************

    GOTO 전진1

    '****************************************
동쪽동쪽소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 0 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 0 !"

    GOSUB SOUND_PLAY_CHK
    WAIT

    RETURN

    '*********************************
서쪽서쪽소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 1 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 1 !"

    GOSUB SOUND_PLAY_CHK
    WAIT

    RETURN

    '**********************************
남쪽남쪽소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 2 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 2 !"

    GOSUB SOUND_PLAY_CHK
    WAIT

    RETURN
    '***********************************
북쪽북쪽소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 3 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 3 !"

    GOSUB SOUND_PLAY_CHK

    RETURN
    '****************************************
위험지역소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 6 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 6 !"

    GOSUB SOUND_PLAY_CHK
    WAIT

    RETURN
    '****************************
B소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 9 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 9 !"

    GOSUB SOUND_PLAY_CHK
    
    WAIT

    RETURN
    '***************************
D소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 11 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 11 !"

    GOSUB SOUND_PLAY_CHK
    
    WAIT

    RETURN
    '**************************
C소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 10 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 10 !"

    GOSUB SOUND_PLAY_CHK

    RETURN	
        '************************************************
A소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 8 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 8 !"

    GOSUB SOUND_PLAY_CHK

    RETURN
    '************************************************
구조요청소리내기:
    PRINT "open 22GongMo.mrs !"

    PRINT "SND 7 !"

    GOSUB SOUND_PLAY_CHK

    PRINT "SND 7 !"

    GOSUB SOUND_PLAY_CHK

    RETURN

   ' *******************************************
양손앞으로나란히들기:
    MOVE G6A, 100,  76, 145,  93, 100,
    MOVE G6D, 100,  76, 145,  93, 100,
    MOVE G6B, 190,  20,  80,  ,  ,
    MOVE G6C, 190,  21,  80,  ,  ,
    WAIT
    DELAY 500
    RETURN
    '************************
양손뒤로나란히들기:
    MOVE G6A, 100,  76, 145,  93, 100,
    MOVE G6D, 100,  76, 145,  93, 100,
    MOVE G6B,  10,  30,  80,  ,  ,
    MOVE G6C,  10,  30,  80,  ,  ,
    WAIT
    DELAY 500
    RETURN
   ' ***********************************
오른팔앞으로들기:
    MOVE G6A, 100,  76, 145,  93, 100,
    MOVE G6D, 100,  76, 145,  93, 100,
    MOVE G6B, 100,  30,  80,  ,  ,
    MOVE G6C, 183,  30,  80,  ,  ,
    WAIT
    DELAY 500
    RETURN
   ' ***************************************
왼팔앞으로들기:
    MOVE G6A, 100,  76, 145,  93, 100,
    MOVE G6D, 100,  76, 145,  93, 100,
    MOVE G6B, 185,  30,  80,  ,  ,
    MOVE G6C, 100,  30,  80,  ,  ,
    WAIT
    DELAY 500
    RETURN
   ' *******************************
팔제자리:
    MOVE G6A,100,  76, 145,  93, 100, 100
    MOVE G6D,100,  76, 145,  93, 100, 100
    MOVE G6B,100,  30,  80,
    MOVE G6C,100,  30,  80
    WAIT
    DELAY 500

    mode = 0
    WAIT
    RETURN
   ' ***************************
만세:
    SPEED 5
    MOVE G6A, 100,  76, 145,  93, 100,
    MOVE G6D, 100,  76, 145,  93, 100,
    MOVE G6B, 100, 170,  80,  ,  ,
    MOVE G6C, 100, 170,  80,  ,  ,
    WAIT
    DELAY 500

    RETURN
    '*****************************************
고개동작:

    SPEED 3

    SERVO 16, UPDOWN
    
    
    WAIT

    RETURN

   ' *********************************
왼쪽횡으로이동:
    
        MOTORMODE G6A,3,3,3,3,2
        MOTORMODE G6D,3,3,3,3,2

        SPEED 12
        MOVE G6A, 95,  90, 125, 100, 104, 100
        MOVE G6D,105,  76, 145,  93, 104, 100
        WAIT

        SPEED 12
        MOVE G6A, 102,  77, 145, 93, 100, 100
        MOVE G6D,90,  80, 140,  95, 107, 100
        WAIT

        SPEED 10
        MOVE G6A,95,  76, 145,  93, 102, 100
        MOVE G6D,95,  76, 145,  93, 102, 100
        WAIT

        SPEED 8
        GOSUB 기본자세2
        GOSUB All_motor_mode3
        WAIT
    
    DELAY 500
    

    RETURN
    '********************************
오른쪽횡으로이동:

        MOTORMODE G6A,3,3,3,3,2
        MOTORMODE G6D,3,3,3,3,2

        SPEED 12
        MOVE G6D, 95,  90, 125, 100, 104, 100
        MOVE G6A,105,  76, 146,  93, 104, 100
        WAIT

        SPEED 12
        MOVE G6D, 102,  77, 145, 93, 100, 100
        MOVE G6A,90,  80, 140,  95, 107, 100
        WAIT

        SPEED 10
        MOVE G6D,95,  76, 145,  93, 102, 100
        MOVE G6A,95,  76, 145,  93, 102, 100
        WAIT

        SPEED 8
        GOSUB 기본자세2
        GOSUB All_motor_mode3
        WAIT
    
    WAIT
	DELAY 500
    RETURN
   ' ******************************************
   집고왼쪽턴20:

    GOSUB Leg_motor_mode2
    SPEED 8
    MOVE G6A,95,  96, 145,  65, 105, 100
    MOVE G6D,95,  56, 145,  105, 105, 100
    WAIT

    SPEED 12
    MOVE G6A,93,  96, 145,  65, 105, 100
    MOVE G6D,93,  56, 145,  105, 105, 100
    WAIT
    SPEED 6
    MOVE G6A,101,  76, 146,  85, 98, 100
    MOVE G6D,101,  76, 146,  85, 98, 100
    WAIT

    MOVE G6A,100,  76, 145,  85, 100
    MOVE G6D,100,  76, 145,  85, 100
    WAIT
    GOSUB Leg_motor_mode1
    
    RETURN
       '**********************************************

왼쪽옆으로70연속:
    MOTORMODE G6A,3,3,3,3,2
    MOTORMODE G6D,3,3,3,3,2

    DELAY  10

    SPEED 10
    MOVE G6A, 90,  90, 120, 105, 110, 100	
    MOVE G6D,100,  76, 145,  93, 107, 100	

    WAIT

    SPEED 13
    MOVE G6A, 102,  76, 145, 93, 100, 100
    MOVE G6D,83,  78, 140,  96, 115, 100
    WAIT

    SPEED 13
    MOVE G6A,98,  76, 145,  93, 100, 100
    MOVE G6D,98,  76, 145,  93, 100, 100
    WAIT

    SPEED 12
    MOVE G6D,100,  76, 145,  93, 100, 100
    MOVE G6A,100,  76, 145,  93, 100, 100
    WAIT

    GOSUB 기본자세2

    RETURN

    '******************************************
오른쪽옆으로70연속:
    MOTORMODE G6A,3,3,3,3,2
    MOTORMODE G6D,3,3,3,3,2


    DELAY  10

    SPEED 10
    MOVE G6D, 90,  90, 120, 105, 110, 100
    MOVE G6A,100,  76, 145,  93, 107, 100

    WAIT

    SPEED 13
    MOVE G6D, 102,  76, 145, 93, 100, 100
    MOVE G6A,83,  78, 140,  96, 115, 100
    WAIT

    SPEED 13
    MOVE G6D,98,  76, 145,  93, 100, 100
    MOVE G6A,98,  76, 145,  93, 100, 100
    WAIT

    SPEED 12
    MOVE G6A,100,  76, 145,  93, 100, 100
    MOVE G6D,100,  76, 145,  93, 100, 100
    WAIT


    GOSUB 기본자세2

    RETURN
    '**********************************************
    
좌회전90도:
    MOTORMODE G6A,3,3,3,3,2
    MOTORMODE G6D,3,3,3,3,2


    SPEED 8
    MOVE G6A,95,  106, 145,  68, 105, 100
    MOVE G6D,95,  46, 145,  118, 105, 100
    WAIT
    DELAY 300

    SPEED 10
    MOVE G6A,93,  106, 145,  68, 105, 100
    MOVE G6D,93,  46, 145,  118, 105, 100
    WAIT

    SPEED 6
    GOSUB 기본자세2
    WAIT

    DELAY 500

    SPEED 8
    MOVE G6A,95,  106, 145,  68, 105, 100
    MOVE G6D,95,  46, 145,  118, 105, 100
    WAIT
   	DELAY 300

    SPEED 10
    MOVE G6A,93,  106, 145,  68, 105, 100
    MOVE G6D,93,  46, 145,  118, 105, 100
    WAIT

    SPEED 6
    GOSUB 기본자세2
    WAIT

    DELAY 500

    SPEED 8
    MOVE G6A,95,  106, 145,  68, 105, 100
    MOVE G6D,95,  46, 145,  118, 105, 100
    WAIT
	DELAY 300
    SPEED 10
    MOVE G6A,93,  106, 145,  68, 105, 100
    MOVE G6D,93,  46, 145,  118, 105, 100
    WAIT

    SPEED 6
    GOSUB 기본자세2

	DELAY 500
    RETURN
   ' ***************************************
좌회전10도:
    MOTORMODE G6A,3,3,3,3,2
    MOTORMODE G6D,3,3,3,3,2
    SPEED 5
    MOVE G6A,97,  86, 145,  83, 103, 100
    MOVE G6D,97,  66, 145,  103, 103, 100
    WAIT

    SPEED 12
    MOVE G6A,94,  86, 145,  83, 101, 100
    MOVE G6D,94,  66, 145,  103, 101, 100
    WAIT

    SPEED 6
    MOVE G6A,101,  76, 146,  93, 98, 100
    MOVE G6D,101,  76, 146,  93, 98, 100
    WAIT

    GOSUB 기본자세2
	DELAY 500
    RETURN
   ' ************************************
우회전10도:
	MOTORMODE G6A,3,3,3,3,2
    MOTORMODE G6D,3,3,3,3,2
    SPEED 5
    MOVE G6A,97,  66, 145,  103, 103, 100
    MOVE G6D,97,  86, 145,  83, 103, 100
    WAIT

    SPEED 12
    MOVE G6A,94,  66, 145,  103, 101, 100
    MOVE G6D,94,  86, 145,  83, 101, 100
    WAIT

    SPEED 6
    MOVE G6A,101,  76, 146,  93, 98, 100
    MOVE G6D,101,  76, 146,  93, 98, 100
    WAIT

    GOSUB 기본자세2
	DELAY 500
    
		RETURN
   ' *********************
우회전90도:

    MOTORMODE G6A,3,3,3,3,2
    MOTORMODE G6D,3,3,3,3,2


    SPEED 8
    MOVE G6A,95,  46, 145,  123, 105, 100
    MOVE G6D,95,  106, 145,  63, 105, 100
    WAIT
	DELAY 200
    SPEED 10
    MOVE G6A,93,  46, 145,  123, 105, 100
    MOVE G6D,93,  106, 145,  63, 105, 100
    WAIT

    SPEED 6
    GOSUB 기본자세2
    WAIT

    DELAY 500

    SPEED 8
    MOVE G6A,95,  46, 145,  123, 105, 100
    MOVE G6D,95,  106, 145,  63, 105, 100
    WAIT
	DELAY 200
    SPEED 10
    MOVE G6A,93,  46, 145,  123, 105, 100
    MOVE G6D,93,  106, 145,  63, 105, 100
    WAIT

    SPEED 6
    GOSUB 기본자세2
    WAIT

    DELAY 500

    SPEED 8
    MOVE G6A,95,  46, 145,  123, 105, 100
    MOVE G6D,95,  106, 145,  63, 105, 100
    WAIT
	DELAY 200
    SPEED 10
    MOVE G6A,93,  46, 145,  123, 105, 100
    MOVE G6D,93,  106, 145,  63, 105, 100
    WAIT

    SPEED 6
    GOSUB 기본자세2

	WAIT
   
    
    RETURN
        '************************************************

    '**********
시민잡기:
    GOSUB 자이로OFF
    SPEED 3
    MOVE G6A,100, 145,  28, 145, 100, 100
    MOVE G6D,100, 145,  28, 145, 100, 100
    MOVE G6B,100,  30,  80,
    MOVE G6C,100,  30,  80
    WAIT
	DELAY 500
	SPEED 3
    MOVE G6A, 100, 146,  45, 148, 100,
    MOVE G6D, 100, 146,  45, 148, 100,
    MOVE G6B, 160,  18,  50,  ,  ,
    MOVE G6C, 160,  18,  50,  ,  ,
    WAIT
	DELAY 500
	SPEED 2
	MOVE G6A,100, 145,  28, 145, 100, 100
    MOVE G6D,100, 145,  28, 145, 100, 100
    WAIT
    DELAY 500
    MOVE G6A,100,  76, 145,  93, 100, 100
    MOVE G6D,100,  76, 145,  93, 100, 100

    RETURN
    '*****************
시민잡고전진:
    GOSUB All_motor_mode3
    보행COUNT = 0
    SPEED 7
    HIGHSPEED SETON

    IF 보행순서 = 0 THEN
        보행순서 = 1
        MOVE G6A,95,  76, 147,  93, 101
        MOVE G6D,101,  76, 147,  93, 98

        WAIT

        GOTO 시민잡고전진1
    ELSE
        보행순서 = 0
        MOVE G6D,95,  76, 147,  93, 101
        MOVE G6A,101,  76, 147,  93, 98

        WAIT

        GOTO 시민잡고전진4
    ENDIF

    '**********************

시민잡고전진1:
    MOVE G6A,95,  90, 125, 100, 104
    MOVE G6D,104,  77, 147,  93,  102

    WAIT

시민잡고전진2:

    MOVE G6A,103,   73, 140, 103,  100
    MOVE G6D, 95,  85, 147,  85, 102
    WAIT

    GOSUB 앞뒤기울기측정
    IF 넘어진확인 = 1 THEN
        넘어진확인 = 0

        RETURN
    ENDIF

    보행COUNT = 보행COUNT + 1
    IF 보행COUNT > 보행횟수 THEN  GOTO 시민잡고전진2_stop

    ERX 4800,A, 시민잡고전진4
    IF A <> A_old THEN
시민잡고전진2_stop:
        MOVE G6D,95,  90, 125, 95, 104
        MOVE G6A,104,  76, 145,  91,  102

        WAIT
		HIGHSPEED SETOFF

        'DELAY 400
        RETURN
    ENDIF

    '*********************************

시민잡고전진4:
    MOVE G6D,95,  95, 120, 100, 104
    MOVE G6A,104,  77, 147,  93,  102

    WAIT

시민잡고전진5:
    MOVE G6D,103,    73, 140, 103,  100
    MOVE G6A, 95,  85, 147,  85, 102
    WAIT

    GOSUB 앞뒤기울기측정
    IF 넘어진확인 = 1 THEN
        넘어진확인 = 0
        RETURN
    ENDIF

    보행COUNT = 보행COUNT + 1
    IF 보행COUNT > 보행횟수 THEN  GOTO 시민잡고전진5_stop

    ERX 4800,A, 시민잡고전진1
    IF A <> A_old THEN
시민잡고전진5_stop:
        MOVE G6A,95,  90, 125, 95, 104
        MOVE G6D,104,  76, 145,  91,  102

        WAIT
        HIGHSPEED SETOFF
       
        
        

        DELAY 400
        RETURN
    ENDIF

    '*************************************

    '*********************************

    GOTO 시민잡고전진1

'*************************************************************************
시민놓기:
    GOSUB 자이로OFF
    SPEED 3
    MOVE G6A,100, 145,  28, 145, 100, 100
    MOVE G6D,100, 145,  28, 145, 100, 100
    WAIT
    DELAY 500
    SPEED 2

    MOVE G6B,155,  30,  80,
    MOVE G6C,155,  30,  80
    WAIT
    DELAY 500
    
    
    
    MOVE G6B,100,  30,  80,
    MOVE G6C,100,  30,  80
    WAIT
    DELAY 500
    GOSUB 기본자세2
    

    RETURN
'*************************************************************************
'*************************** 기본 제공 label *******************************
'*************************************************************************
'*************************************************************************

MOTOR_ON:
    GOSUB MOTOR_GET

    MOTOR G6B
    DELAY 50
    MOTOR G6C
    DELAY 50
    MOTOR G6A
    DELAY 50
    MOTOR G6D

    모터ONOFF = 0
    GOSUB 시작음

    RETURN
    '************************************************
MOTOR_GET:
    GETMOTORSET G6A,1,1,1,1,1,0
    GETMOTORSET G6B,1,1,1,0,0,1
    GETMOTORSET G6C,1,1,1,0,1,0
    GETMOTORSET G6D,1,1,1,1,1,0

    RETURN
    '************************************************
All_motor_Reset:
    MOTORMODE G6A,1,1,1,1,1,1
    MOTORMODE G6D,1,1,1,1,1,1
    MOTORMODE G6B,1,1,1,,,1
    MOTORMODE G6C,1,1,1,,1

    RETURN
    '************************************************
Leg_motor_mode2:
    MOTORMODE G6A,2,2,2,2,2
    MOTORMODE G6D,2,2,2,2,2

    RETURN
    '************************************************
Leg_motor_mode3:
    MOTORMODE G6A,3,3,3,3,3
    MOTORMODE G6D,3,3,3,3,3

    RETURN
    '************************************************
All_motor_mode2:

    MOTORMODE G6A,2,2,2,2,2
    MOTORMODE G6D,2,2,2,2,2
    MOTORMODE G6B,2,2,2,,,2
    MOTORMODE G6C,2,2,2,,2

    RETURN
    '************************************************
All_motor_mode3:

    MOTORMODE G6A,3,3,3,3,3
    MOTORMODE G6D,3,3,3,3,3
    MOTORMODE G6B,3,3,3,,,3
    MOTORMODE G6C,3,3,3,,3

    RETURN
    '************************************************
전원초기자세:
    MOVE G6A,100,  76, 145,  93, 100, 100
    MOVE G6D,100,  76, 145,  93, 100, 100
    MOVE G6B,100,  35,  90,
    MOVE G6C,100,  35,  90
    WAIT

    mode = 0

    RETURN
    '************************************************
자이로INIT:

    GYRODIR G6A, 0, 0, 1, 0,0
    GYRODIR G6D, 1, 0, 1, 0,0

    GYROSENSE G6A,200,150,30,150,0
    GYROSENSE G6D,200,150,30,150,0

    RETURN
    '***********************************************
    '**** 자이로감도 설정 ****
자이로MAX:
    GYROSENSE G6A,250,180,30,180,0
    GYROSENSE G6D,250,180,30,180,0

    RETURN
    '***********************************************
자이로MID:
    GYROSENSE G6A,200,150,30,150,0
    GYROSENSE G6D,200,150,30,150,0

    RETURN
    '***********************************************
자이로MIN:
    GYROSENSE G6A,200,100,30,100,0
    GYROSENSE G6D,200,100,30,100,0

    RETURN
    '***********************************************
자이로ON:
    GYROSET G6A, 4, 3, 3, 3, 0
    GYROSET G6D, 4, 3, 3, 3, 0

    자이로ONOFF = 1

    RETURN
    '***********************************************
자이로OFF:
    GYROSET G6A, 0, 0, 0, 0, 0
    GYROSET G6D, 0, 0, 0, 0, 0

    자이로ONOFF = 0

    RETURN
    '************************************************
시작음:
    TEMPO 220
    MUSIC "O23EAB7EA>3#C"
    RETURN
    '************************************************
기본자세2:
    MOVE G6A,100,  76, 145,  93, 100, 100
    MOVE G6D,100,  76, 145,  93, 100, 100
    MOVE G6B,100,  30,  80,
    MOVE G6C,100,  30,  80
    WAIT

    mode = 0
    RETURN
    '*************************************************
종료음:
    TEMPO 220
    MUSIC "O38GD<BGD<BG"
    RETURN
    '************************************************
에러음:
    TEMPO 250
    MUSIC "FFF"
    RETURN

    '************************************************
안정화자세:
    MOVE G6A,98,  76, 145,  93, 101, 100
    MOVE G6D,98,  76, 145,  93, 101, 100
    MOVE G6B,100,  35,  90,
    MOVE G6C,100,  35,  90
    WAIT
    mode = 0

    RETURN
    '************************************************

NUM_TO_ARR:
    NO_4 =  BUTTON_NO / 10000
    TEMP_INTEGER = BUTTON_NO MOD 10000

    NO_3 =  TEMP_INTEGER / 1000
    TEMP_INTEGER = BUTTON_NO MOD 1000

    NO_2 =  TEMP_INTEGER / 100
    TEMP_INTEGER = BUTTON_NO MOD 100

    NO_1 =  TEMP_INTEGER / 10
    TEMP_INTEGER = BUTTON_NO MOD 10

    NO_0 =  TEMP_INTEGER

    RETURN
    '************************************************
Number_Play:
    GOSUB NUM_TO_ARR

    PRINT "NPL "
    '*************
    NUM = NO_4
    GOSUB NUM_1_9
    '*************
    NUM = NO_3
    GOSUB NUM_1_9
    '*************
    NUM = NO_2
    GOSUB NUM_1_9
    '*************
    NUM = NO_1
    GOSUB NUM_1_9
    '*************
    NUM = NO_0
    GOSUB NUM_1_9
    PRINT " !"

    GOSUB SOUND_PLAY_CHK
    PRINT "SND 16 !"
    GOSUB SOUND_PLAY_CHK

    RETURN
    '************************************************
SOUND_PLAY_CHK:
    DELAY 60
    SOUND_BUSY = IN(46)
    IF SOUND_BUSY = 1 THEN GOTO SOUND_PLAY_CHK
    DELAY 50

    RETURN
    '************************************************
NUM_1_9:
    IF NUM = 1 THEN
        PRINT "1"
    ELSEIF NUM = 2 THEN
        PRINT "2"
    ELSEIF NUM = 3 THEN
        PRINT "3"
    ELSEIF NUM = 4 THEN
        PRINT "4"
    ELSEIF NUM = 5 THEN
        PRINT "5"
    ELSEIF NUM = 6 THEN
        PRINT "6"
    ELSEIF NUM = 7 THEN
        PRINT "7"
    ELSEIF NUM = 8 THEN
        PRINT "8"
    ELSEIF NUM = 9 THEN
        PRINT "9"
    ELSEIF NUM = 0 THEN
        PRINT "0"
    ENDIF

    RETURN
    '************************************************
        '**********************************************
집고오른쪽턴45:

    GOSUB Leg_motor_mode2
    SPEED 8
    MOVE G6A,95,  46, 145,  115, 105, 100
    MOVE G6D,95,  106, 145,  55, 105, 100
    WAIT

    SPEED 10
    MOVE G6A,93,  46, 145,  115, 105, 100
    MOVE G6D,93,  106, 145,  55, 105, 100
    WAIT

    SPEED 8
    MOVE G6A,100,  76, 145,  85, 100
    MOVE G6D,100,  76, 145,  85, 100
    WAIT
    GOSUB Leg_motor_mode1
    RETURN

    '************************************************
    '************************************************

앞뒤기울기측정:
    FOR i = 0 TO COUNT_MAX
        A = AD(앞뒤기울기AD포트)	'기울기 앞뒤
        IF A > 250 OR A < 5 THEN RETURN
        IF A > MIN AND A < MAX THEN RETURN
        DELAY 기울기확인시간
    NEXT i

    IF A < MIN THEN
        GOSUB 기울기앞
    ELSEIF A > MAX THEN
        GOSUB 기울기뒤
    ENDIF

    RETURN
    '**************************************************
좌우기울기측정:
    FOR i = 0 TO COUNT_MAX
        B = AD(좌우기울기AD포트)	'기울기 좌우
        IF B > 250 OR B < 5 THEN RETURN
        IF B > MIN AND B < MAX THEN RETURN
        DELAY 기울기확인시간
    NEXT i

    IF B < MIN OR B > MAX THEN
        SPEED 8
        MOVE G6B,140,  40,  80
        MOVE G6C,140,  40,  80
        WAIT
        GOSUB 기본자세	
    ENDIF

    RETURN
    '**************************************************
적외선거리센서확인:
    적외선거리값 = AD(적외선AD포트)

    IF 적외선거리값 > 50 THEN '50 = 적외선거리값 = 25cm
        MUSIC "C"
        DELAY 200
    ENDIF

    RETURN
    ' ************************************************
기울기앞:
    A = AD(앞뒤기울기AD포트)
    'IF A < MIN THEN GOSUB 앞으로일어나기
    IF A < MIN THEN
        ETX  4800,16
        GOSUB 뒤로일어나기
    ENDIF

    RETURN
    '**************************************************
기울기뒤:
    A = AD(앞뒤기울기AD포트)
    'IF A > MAX THEN GOSUB 뒤로일어나기
    IF A > MAX THEN
        ETX  4800,15
        GOSUB 앞으로일어나기
    ENDIF

    RETURN
    '**************************************************
앞으로일어나기:
    HIGHSPEED SETOFF
    PTP SETON 				
    PTP ALLON

    GOSUB 자이로OFF

    HIGHSPEED SETOFF

    GOSUB All_motor_Reset

    SPEED 15
    MOVE G6A,100, 15,  70, 140, 100,
    MOVE G6D,100, 15,  70, 140, 100,
    MOVE G6B,20,  140,  15
    MOVE G6C,20,  140,  15
    WAIT

    SPEED 12
    MOVE G6A,100, 136,  35, 80, 100,
    MOVE G6D,100, 136,  35, 80, 100,
    MOVE G6B,20,  30,  80
    MOVE G6C,20,  30,  80
    WAIT

    SPEED 12
    MOVE G6A,100, 165,  70, 30, 100,
    MOVE G6D,100, 165,  70, 30, 100,
    MOVE G6B,30,  20,  95
    MOVE G6C,30,  20,  95
    WAIT

    GOSUB Leg_motor_mode3

    SPEED 10
    MOVE G6A,100, 165,  45, 90, 100,
    MOVE G6D,100, 165,  45, 90, 100,
    MOVE G6B,130,  50,  60
    MOVE G6C,130,  50,  60
    WAIT

    SPEED 6
    MOVE G6A,100, 145,  45, 130, 100,
    MOVE G6D,100, 145,  45, 130, 100,
    WAIT

    SPEED 8
    GOSUB All_motor_mode2
    GOSUB 기본자세
    넘어진확인 = 1

    DELAY 200
    GOSUB 자이로ON

    RETURN
    '***********************************************
뒤로일어나기:
    HIGHSPEED SETOFF
    PTP SETON 				
    PTP ALLON		

    GOSUB 자이로OFF

    GOSUB All_motor_Reset

    SPEED 15
    GOSUB 기본자세

    MOVE G6A,90, 130, ,  80, 110, 100
    MOVE G6D,90, 130, 120,  80, 110, 100
    MOVE G6B,150, 160,  10, 100, 100, 100
    MOVE G6C,150, 160,  10, 100, 100, 100
    WAIT

    MOVE G6B,170, 140,  10, 100, 100, 100
    MOVE G6C,170, 140,  10, 100, 100, 100
    WAIT

    MOVE G6B,185,  20, 70,  100, 100, 100
    MOVE G6C,185,  20, 70,  100, 100, 100
    WAIT

    SPEED 10
    MOVE G6A, 80, 155,  85, 150, 150, 100
    MOVE G6D, 80, 155,  85, 150, 150, 100
    MOVE G6B,185,  20, 70,  100, 100, 100
    MOVE G6C,185,  20, 70,  100, 100, 100
    WAIT

    MOVE G6A, 75, 162,  55, 162, 155, 100
    MOVE G6D, 75, 162,  59, 162, 155, 100
    MOVE G6B,188,  10, 100, 100, 100, 100
    MOVE G6C,188,  10, 100, 100, 100, 100
    WAIT

    SPEED 10
    MOVE G6A, 60, 162,  30, 162, 145, 100
    MOVE G6D, 60, 162,  30, 162, 145, 100
    MOVE G6B,170,  10, 100, 100, 100, 100
    MOVE G6C,170,  10, 100, 100, 100, 100
    WAIT

    GOSUB Leg_motor_mode3	

    MOVE G6A, 60, 150,  28, 155, 140, 100
    MOVE G6D, 60, 150,  28, 155, 140, 100
    MOVE G6B,150,  60,  90, 100, 100, 100
    MOVE G6C,150,  60,  90, 100, 100, 100
    WAIT

    MOVE G6A,100, 150,  28, 140, 100, 100
    MOVE G6D,100, 150,  28, 140, 100, 100
    MOVE G6B,130,  50,  85, 100, 100, 100
    MOVE G6C,130,  50,  85, 100, 100, 100
    WAIT

    DELAY 100

    MOVE G6A,100, 150,  33, 140, 100, 100
    MOVE G6D,100, 150,  33, 140, 100, 100
    WAIT
    SPEED 10
    GOSUB 기본자세

    넘어진확인 = 1

    DELAY 200
    GOSUB 자이로ON

    RETURN
    '************************************************
기본자세:
    MOVE G6A,100,  76, 145,  93, 100, 100
    MOVE G6D,100,  76, 145,  93, 100, 100
    MOVE G6B,100,  30,  80,
    MOVE G6C,100,  30,  80,
    WAIT

    mode = 0

    RETURN
        '************************************************
Leg_motor_mode1:
    MOTORMODE G6A,1,1,1,1,1
    MOTORMODE G6D,1,1,1,1,1
    RETURN
    '************************************************
