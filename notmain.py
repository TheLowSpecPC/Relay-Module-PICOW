import time
import network
from machine import Pin
from umqtt.simple import MQTTClient
from secret import ssid, password

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
    time.sleep(1)
status = wlan.ifconfig()
print('connection to', ssid,'succesfull established!')
print('IP-adress: ' + status[0])

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "io.adafruit.com"
mqtt_username = "TheLowSpecPC"  # Your Adafruit IO username
mqtt_password = "aio_oqNV12FqGxGzk9Fnk0SWIxFJOFxP"  # Adafruit IO Key
relay1_toggle = "TheLowSpecPC/feeds/toggle"
timer_toggle = "TheLowSpecPC/feeds/timer"
hours_feed = "TheLowSpecPC/feeds/hours"
minutes_feed = "TheLowSpecPC/feeds/minutes"

hours = ''
minutes = ''

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
                hours = hr.read()
                hr.close()
            with open('minutes.txt', 'r') as mr:
                minutes = mr.read()
                mr.close()
            print(hours+":"+minutes)

# Before connecting, tell the MQTT client to use the callback
mqtt_client.set_callback(toggle)

try:
    mqtt_client.connect()
except OSError as e:
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
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