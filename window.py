import win32api as win32
import win32con
import serial
import time
#시리얼 연결
ser = serial.Serial(
    port='COM3',\
    baudrate=115200,\
    timeout=None)
print("connected to: " + ser.portstr)

#모니터 목록 출력 함수
def printAllScreen():
    i = 0
    while True:
        try:
            device = win32.EnumDisplayDevices(None,i)
            print("[%d] %s (%s)"%(i,device.DeviceString,device.DeviceName))
            i = i+1
        except:
            break
    return i

#4번 선택(보조 모니터)
monitor = win32.EnumDisplayDevices(None, 4) 


#DMDO_DEFAULT(0) - 디스플레이 기본 상태
#DMDO_90(1) - 시계방향 90도 회전
#DMDO_180(2) - 시계방향 180도 회전
#DMDO_270(3) - 시계방향 270도 회전

rotation = 0
rotation_flag = 0
#현재 설정 저장, 실패시 0리턴
dm = win32.EnumDisplaySettings(monitor.DeviceName, win32con.ENUM_CURRENT_SETTINGS) #디스플레이 현새 세팅 불러오기
ser.flush()
for i in range(50): #프로그램 실행시 각도가 낮게 잡히는 문제 수정을 위해 추가
        b = ser.readline()
while True:
    try:
        b = ser.readline() #자이로센서의 현재 기준값 지정
        past = float(b.decode()) #문자열을 float형으로 변경
        break
    except:
        continue #값이 아닐경우 값이 나올때까지 반복
    
while True:
    b = ser.read(ser.inWaiting())
    if(b == ''.encode()): #''를 읽었을시 다시 읽음
        continue
    try:
        num = float(b.decode())
        #print(num)
        if abs(past - num)>10: #이전값과 10도 이상 차이날경우 값이 튕긴거로 판단, 값을 다시 읽음
            continue
        else:
            past = num #정상값일경우 이전값 저장
        if dm.DisplayOrientation == win32con.DMDO_DEFAULT: #현재모니터 화면이 기본상태일때 (0도)
            if num > 50: #시계방향 50도 이상 회전시
                rotation = win32con.DMDO_90
                rotation_flag = 1 #회전 발생 플래그
            elif num < -50: #반시계방향 50도 이상 회전시
                rotation = win32con.DMDO_270
                rotation_flag = 1 #회전 발생 플래그

        elif dm.DisplayOrientation == win32con.DMDO_90 : #현재모니터 화면이 90도 회전상태일때(시계방향)
            if num < 40 : #원래 상태로 돌렸다고 판단
                rotation = win32con.DMDO_DEFAULT
                rotation_flag = 1 #회전 발생 플래그

        elif dm.DisplayOrientation == win32con.DMDO_270: #현재모니터 화면이 270도회전상태일때(반시계방향)
            if num > -40 : #원래 상태로 돌렸다고 판단
                rotation = win32con.DMDO_DEFAULT
                rotation_flag = 1 #회전 발생 플래그

    except Exception as e:
        continue




    if rotation_flag == 1 :
        if((dm.DisplayOrientation + rotation)%2 == 1):
            #가로세로 변경
            dm.PelsWidth, dm.PelsHeight = dm.PelsHeight, dm.PelsWidth

        dm.DisplayOrientation = rotation #현재 상태 저장
        win32.ChangeDisplaySettingsEx(monitor.DeviceName, dm) #화면 변경
        rotation_flag = 0

    time.sleep(0.01)