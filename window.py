import win32api as win32
import win32con
import serial

#시리얼 연결
ser = serial.Serial(
    port='COM11',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)
print("connected to: " + ser.portstr)

#모니터 목록 출력
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

#0번 선택(주모니터)
monitor = win32.EnumDisplayDevices(None, 0) 


#DMDO_DEFAULT(0) - 디스플레이 기본 상태
#DMDO_90(1) - 시계방향 90도 회전
#DMDO_180(2) - 시계방향 180도 회전
#DMDO_270(3) - 시계방향 270도 회전

rotation = 0
rotation_flag = 0

#현재 설정 저장, 실패시 0리턴
dm = win32.EnumDisplaySettings(monitor.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
seq = []
while True:
    for c in ser.read():
        seq.append(chr(c)) #convert from ANSII
        
        joined_seq = ''.join(str(v) for v in seq) #Make a string from array

        if chr(c) == '\n':
            #print(float(joined_seq))
            num = float(joined_seq)
            print(num)
            if dm.DisplayOrientation == win32con.DMDO_DEFAULT: #기본상태일때
                if num > 50: #시계방향 50도 이상 회전시
                    rotation = win32con.DMDO_90
                    rotation_flag = 1
                elif num < -50: #반시계방향 50도 이상 회전시
                    rotation = win32con.DMDO_270
                    rotation_flag = 1

            elif dm.DisplayOrientation == win32con.DMDO_90 : #90도 회전상태일때
                if num < 40 : #원래 상태로 간주
                    rotation = win32con.DMDO_DEFAULT
                    rotation_flag = 1

            elif dm.DisplayOrientation == win32con.DMDO_270: #279도회전상태일때
                if num > -40 : #원래상태로 간주
                    rotation = win32con.DMDO_DEFAULT
                    rotation_flag = 1
            seq = []
            break
    if rotation_flag == 1 :
        #가로세로 변경
        if((dm.DisplayOrientation + rotation)%2 == 1):
            dm.PelsWidth, dm.PelsHeight = dm.PelsHeight, dm.PelsWidth

        dm.DisplayOrientation = rotation
        win32.ChangeDisplaySettingsEx(monitor.DeviceName, dm)
    rotation_flag = 0