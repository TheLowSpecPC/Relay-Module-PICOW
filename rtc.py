import network
import secret
from machine import RTC
from time import sleep
import ntptime
import utime as time

ssid = secret.ssid
password = secret.password

# NTP-Host
NTP_HOST = 'pool.ntp.org'

# Funktion: get time from NTP Server
def getTimeNTP(UTC_OFFSET=+5):
    ntptime.settime()
    return time.gmtime(time.time() + (UTC_OFFSET * 3600)+1800)

# Funktion: copy time to PI pico´s RTC
def setTimeRTC():
    tm = getTimeNTP()
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    
def check_alarm(set_year,set_month,set_day,set_hour,set_minute):
    time = rtc.datetime()
    if set_year == int(time[0]) and set_month == int(time[1]) and set_day == int(time[2]) and set_hour == int(time[4]) and set_minute == int(time[5]):
        print("ALARM")
    else:
        print("Time not reached")
        print("time now " + str(time))
        print("time to alarm:  " + str(set_year) +" " + str(set_month) + " " + str(set_day) + " " + str(set_hour) + " " + str(set_minute))

  
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
status = wlan.ifconfig()
print('connection to', ssid,'succesfull established!')
print('IP-adress: ' + status[0])
    

rtc = RTC()  

# Zeit setzen
setTimeRTC()

# Aktuelles Datum ausgeben
print()
print(rtc.datetime())

while True:
    print(rtc.datetime())
    sleep(2)
#    year=2023
#    month=1
#    day=20
#    hour=20
#    minute=18
#    check_alarm(year,month,day,hour,minute)
#    sleep(10)




