#!/usr/bin/python
from client_mqtt import ClientMQTT
from threading import Thread
import sys,time,re,datetime,json,socket,errno
from pymongo import MongoClient
from socket import error as socket_error

# Set Decimal Precision
from decimal import *
getcontext().prec = 2

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

#Mongo Server
MONGO_IP = '192.168.1.9'
MONGO_PORT = 27017

#Setup Amp Channel Names
channels = ["infeed", "soaker", "dryerMain", "dryerOut", "grinder", "classifier"]

def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

def send_command(req, encoding):
    """Send either Decimal or Hex command to NCD Current Monitor.

    Parameters
    ----------
    req : string
        string containging either complete HEX code for command or Decimal Format from NCD API
    encoding : string
        string containing either "hex" or "dec"

    Returns
    -------
    string
        returns data from Current Monitor

    """
    req = req.decode(encoding)
    s = socket.socket()
    s.settimeout(6)
    try:
        s.connect((TCP_IP, TCP_PORT))
        s.send(req)
        data = s.recv(BUFFER_SIZE)
    except socket.error as e:
        # if e.errno != errno.ECONNREFUSE:
        #     dump(e)
        #     # Not the error we are looking for, re-raise
        #     raise e
        time.sleep(sleep_time)
        s.connect((TCP_IP, TCP_PORT))
        s.send(req)
        data = s.recv(BUFFER_SIZE)
        # print "socket connection refused"
        dump(e)
    # s.connect((TCP_IP, TCP_PORT))
    # s.send(req)
    # data = s.recv(BUFFER_SIZE)
    s.close()
    return data


# Read current and return bytes
def readCurrent():
    """Reads NCD Current Monitor Value and breaks data into pairs for calculations.

    Returns
    -------
    type
        Pairs of data for given current channel.

    """

    # Set Command to be sent to Current Monitor
    # In this case query all 6 channels | https://ncd.io/communicating-to-current-monitoring-controllers/
    MESSAGE = 'aa0ebc320a54926a010106000004551374'
    #MESSAGE = 'AA03FE7C0128'.decode('hex')

    try:
        data = send_command(MESSAGE, 'hex')
        while len(data) < 1:
            data = send_command(MESSAGE, 'hex')
    except socket.timeout as e:
        time.sleep(sleep_time)
        data = send_command(MESSAGE, 'hex')
        print "socket connection died"
        dump(e)
    except socket.error as e:
        dump(e)
        # if e.errno != errno.ECONNREFUSE:
        #     # Not the error we are looking for, re-raise
        #     raise e
        time.sleep(sleep_time)
        data = send_command(MESSAGE, 'hex')
        print "socket connection refused"
        dump(e)

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

        try:
            mid = most + 1
            low = mid + 1
            # Calc channel amp value 3 bytes per channel
            channel[channels[int(count) - 1]] = str( round( ( round(int(dataPairs[most],16) * 65536,1) + round(int(dataPairs[mid],16) * 265,1) + round(int(dataPairs[low],16),1)) / 1000, 1) )
            count = count + 1
            most = most + 3
        except IndexError:
            pass

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
            ampData = json.dumps(channelData)

            #write mqtt channel
            write_mqtt(mqtt_topic, ampData)

            if float(channelData['classifier']) > 1 and float(channelData['classifier']) < 50:	            
	            #Save data to MONGODB
	            mongo = MongoClient(MONGO_IP, MONGO_PORT)
	            mongoDB = mongo['washline']
	            ampdata  = mongoDB.amps
	            ampdata_id = ampdata.insert_one(channelData).inserted_id
            
            time.sleep(sleep_time)

        except IndexError:
            print('ERROR|Value')
            #read Current Data
            data = readCurrent()
            channelData = calcAmps(data)
            channelData['time'] = str(datetime.datetime.now())
            ampData = json.dumps(channelData)

            # publish current data
            write_mqtt(mqtt_topic, ampData)

            #Save data to MONGODB
            mongo = MongoClient(MONGO_IP, MONGO_PORT)
            mongoDB = mongo['washline']
            ampdata  = mongoDB.amps
            ampdata_id = ampdata.insert_one(channelData).inserted_id


            time.sleep(sleep_time)

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
