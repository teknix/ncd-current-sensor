#!/usr/bin/python
from client_mqtt import ClientMQTT
from threading import Thread
import sys,time,re,datetime,json,socket


# Set NCD Current Monitor IP address 
TCP_IP = '192.168.1.102'
# Set Listening Port on Remote Current Monitor
TCP_PORT = 2101
# Set Buffer Size
BUFFER_SIZE = 1024
#Number of Current Monitor Channels
chanNum = 6

#MQTT Topic
mqtt_topic = 'amps'
#MQTT Server IP or HOSTNAME
mqtt_server = '192.168.1.10'
#MQTT Port Number, usally 1883
mqtt_port = 1883
#How long of a sample window (in seconds)
sleep_time = 2 # 2 seconds



#Setup Amp Channel Names
channels = ["infeed", "soaker", "dryerMain", "dryerOut", "grinder", "classifier"]

# Read current and return bytes
def readCurrent():
    # Set Command to be sent to Current Monitor
    # In this case query all 6 channels | https://ncd.io/communicating-to-current-monitoring-controllers/
    MESSAGE = 'aa0ebc320a54926a010106000004551374'.decode('hex')
    #MESSAGE = 'AA03FE7C0128'.decode('hex')

    #Create Socket
    s = socket.socket()
    s.connect((TCP_IP, TCP_PORT))
    # Send Message to Current Monitor
    s.send(MESSAGE)
    # Collect response data
    data = s.recv(BUFFER_SIZE)
    s.close()
    # Convert response to hex
    data = data.encode('hex')
    #Split into Byte Pairs
    pairs = re.findall('..?', data)
    return pairs


def calcAmps(dataPairs):
    count = 1
    channel = {}
    most = 2
    while (count <= chanNum):
        
        mid = most + 1
        low = mid + 1
        # Calc channel amp value 3 bytes per channel
        channel[channels[int(count) - 1]] = str(float((int(dataPairs[most],16)*65536) + (int(dataPairs[mid],16) * 265) + int(dataPairs[low],16)) / 1000)
        count = count + 1
        most = most + 3

    return channel

def write_mqtt(topic, payload):
    mqtt_client = ClientMQTT(ip_address=mqtt_server, port=mqtt_port)
    mqtt_client.publish(topic, payload)


def start_server_mqtt():
    print('Connecting MQTT Client on port ' + mqtt_port)
    mqtt_client = ClientMQTT(ip_address=mqtt_server, port=mqtt_port)
    mqtt_client.simulate()

def start_server_monitor():

    while True:

        try:
            #read Current Data
            data = readCurrent()
            channelData = calcAmps(data)
            channelData['time'] = str(datetime.datetime.now())
            jsonData = json.dumps(channelData)

            # publish current data
            write_mqtt(mqtt_topic, jsonData)
            time.sleep(sleep_time)

        except ValueError:
            print('ERROR|Value')

    return


def main():
    try:
        st = Thread(target=start_server_monitor, args=())
        st.start()

    except (KeyboardInterrupt):
        print "Interrupt received"
        # cleanup()
        raise SystemExit


    # Used for just throwing data at the MQTT server from the IOx application
    # mt = Thread(target=start_server_mqtt, args=())
    # mt.start()


if __name__ == '__main__':
    main()
