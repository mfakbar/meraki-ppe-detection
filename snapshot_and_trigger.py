# import the necessary libraries: requests, json, times, datetime, mqtt, meraki
from datetime import datetime
import paho.mqtt.client as mqtt
import requests
import time
import json

# insert the necessary Meraki variables: meraki api_key, camera SN, meraki base_url, network ID
MV_API_KEY = ""
MV_CAMERA_SN = ["XXXX-XXXX-XXXX"]  # to import a list of camera SNs
MV_BASE_URL = "https://api.meraki.com/api/v1/devices/{0}"

# insert MQTT server variables: Server url, port number
MQTT_SERVER = "test.mosquitto.org"  # this is a public MQTT server for testing
MQTT_PORT = "1883"
MQTT_TOPIC = "/merakimv/{0}/0"

AWS_API_URL = "AWS_API_ENDPOINT"


# get function to extract the MV name from the known SN:
def get_mv_name(serial_number):
    url = MV_BASE_URL.format(serial_number)
    payload = None
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": MV_API_KEY
    }
    response = requests.request('GET', url, headers=headers, data=payload)
    mv_name = response.json()["name"]
    return mv_name


# function to take a snapshot from meraki camera, provided the camera SN, without meraki library
def mv_snapshot_requests_lib(serial_number, sleep_amount):
    time.sleep(sleep_amount)
    headers = {'Content-Type': "application/json",
               'Accept': "application/json",
               'X-Cisco-Meraki-API-Key': MV_API_KEY,
               "timestamp": datetime.now().isoformat()
               }

    base_url = MV_BASE_URL+"/camera/generateSnapshot".format(serial_number)
    snap_url = requests.post(url=base_url, headers=headers).json()["url"]

    # check if the image url is accessible
    for i in range(5):
        # wait for a short time until the snapshot is renderized
        time.sleep(3)

        # check if snapshot is accessible
        image_response = requests.get(snap_url)

        # If HTTP code 200 (OK) is returned, quit the loop and continue
        if image_response.status_code == 200:
            break
        else:
            print(
                f"Could not access snapshot for camera {serial_number} right now. Wait for 3 sec.")
            continue

    print("Snapshot taken! URL: " + snap_url.text.encode('utf8'))
    return snap_url


# callback function to subscribe to MQTT server to listen for event with cameras serial_number
# with multiple camera, we need to subscripe to all their MQTT topics:
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("\n")
    for serial_number in MV_CAMERA_SN:
        client.subscribe(MQTT_TOPIC.format(serial_number))


# callback function when people detection event is received from mqtt server
# check the topic for camera SN and store it as variable for the snapshot function
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    payload_dict = json.loads(payload)

    # extract the camera SN from the mqtt topic header and use it to generate MV snapshot. Generate
    # the time of snapshot by converting the epoc time in the mqtt message
    # create a payload of url, mv name, time of trigger and serial number:
    serial_number = msg.topic.split("/")[2]
    print("Alert from camera SN:" + serial_number)

    if payload_dict['counts']['person'] > 0:
        print("People detected on camera")
        image_url = mv_snapshot_requests_lib(serial_number, 2)
        mv_name = get_mv_name(serial_number)
        time_of_trigger = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(payload_dict['ts']))

        payload = {
            "serial_number": serial_number,
            "snapshot_url": image_url,
            "mv_loc": mv_name,
            "event_time": time_of_trigger
        }

        # Trigger AWS lambda function
        requests.post(url=AWS_API_URL, data=json.dumps(payload)).json()
        time.sleep(60)

        print("Lambda function triggered!")


# instantiate mqtt subscription. I create the client object, bind callback to callback function
# connect to the mqtt broker and run the loop
if __name__ == "__main__":
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_SERVER, MQTT_PORT, 60)
        client.loop_forever()

    except Exception as ex:
        print(
            "[MQTT] failed to connect or receive msg from mqtt, due to: \n {0}".format(ex))
