from time import sleep
import network
from machine import Pin
from umqtt.simple import MQTTClient
from machine import RTC
from secret import ssid, password

rtc = RTC()

# Setup the onboard LED so we can turn it on/off
led = Pin("LED", Pin.OUT)

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = ssid
wifi_password = password

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    sleep(1)
status = wlan.ifconfig()
print('connection to', ssid,'succesfull established!')
print('IP-adress: ' + status[0])

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "io.adafruit.com"
mqtt_username = "TheLowSpecPC"  # Your Adafruit IO username
mqtt_password = "aio_YVvj55rpthSeASH0h6A9vK1FzC3D"  # Adafruit IO Key
relay1_toggle = "TheLowSpecPC/feeds/toggle"
timer_toggle = "TheLowSpecPC/feeds/timer"
hours_feed = "TheLowSpecPC/feeds/hours"
minutes_feed = "TheLowSpecPC/feeds/minutes"

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "somethingreallyrandomandunique123"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

# So that we can respond to messages on an MQTT topic, we need a callback
# function that will handle the messages.
def toggle(topic, message):
    if topic == b'TheLowSpecPC/feeds/toggle':
        print (f'Topic {topic} received message {message}')  # Debug print out of what was received over MQTT
        if message == b'on':
            print("LED ON")
            led.value(1)
        elif message == b'off':
            print("LED OFF")
            led.value(0)
            
    elif topic == b'TheLowSpecPC/feeds/hours':
        print (f'Topic {topic} received message {message}')
        with open('hours.txt', 'w') as hw:
            hw.write(message.decode())
            hw.close()
        
    elif topic == b'TheLowSpecPC/feeds/minutes':
        print (f'Topic {topic} received message {message}')
        with open('minutes.txt', 'w') as mw:
            mw.write(message.decode())
            mw.close()
            
    elif topic == b'TheLowSpecPC/feeds/timer':
        print (f'Topic {topic} received message {message}')
        
        if message == b'start':
            with open('hours.txt', 'r') as hr:
                hrs = hr.read()
                hr.close()
            with open('minutes.txt', 'r') as mr:
                mins = mr.read()
                mr.close()
            startTime = rtc.datetime()
            day = startTime[2]
            hours = startTime[4] + int(hrs)
            minutes = startTime[5] + int(mins)
            
            if int(hrs) > 23:
                day = day+1
            if hours > 23:
                hours = hours-24
            if minutes > 60:
                minutes = minutes-60
            
            a=0
            while a==0:
                endTime = rtc.datetime()
                if endTime[2]==day and endTime[4]==hours and endTime[5]==minutes:
                    a = a+1
                    mqtt_client.publish(timer_toggle, "stop")
                mqtt_client.check_msg()
                sleep(20)
                

# Before connecting, tell the MQTT client to use the callback
mqtt_client.set_callback(toggle)

try:
    mqtt_client.connect()
except OSError as e:
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    sleep(5)
    machine.reset()

# Set the initial state of the LED to off, and let the MQTT topic know about it
led.value(0)
mqtt_client.publish(relay1_toggle, "off")
mqtt_client.publish(timer_toggle, "stop")

# Once connected, subscribe to the MQTT topic
mqtt_client.subscribe(relay1_toggle)
mqtt_client.subscribe(timer_toggle)
mqtt_client.subscribe(hours_feed)
mqtt_client.subscribe(minutes_feed)
print("Connected and subscribed")

try:
    while True:
        # Infinitely wait for messages on the topic.
        # Note wait_msg() is a blocking call, if you're doing multiple things
        # on the Pico you may want to look at putting this on another thread.
        print(f'Waiting for messages')
        mqtt_client.wait_msg()
except Exception as e:
    print(f'Failed to wait for MQTT messages: {e}')
finally:
    mqtt_client.disconnect()