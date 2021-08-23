import boto3
import json
import time
from webex import *
from urllib.request import urlopen
import requests

# AWS
ACCESS_KEY = 'AKIA5ANNF62AWAH7HREH'
SECRET_KEY = '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'


# snapshot_url = event['image_url']
snapshot_url = "https://thumbs.dreamstime.com/b/seaman-ab-bosun-deck-vessel-ship-wearing-ppe-personal-protective-equipment-helmet-coverall-lifejacket-goggles-safety-141609777.jpg"

ppe_requirement = ['FACE_COVER', 'HAND_COVER', 'HEAD_COVER']


def image_encoder(url):
    contents = urlopen(url).read()
    return contents


# Perform connection to AWS Rekognition service
rekog = boto3.client('rekognition', region_name='ap-southeast-1',
                     aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

response = rekog.detect_protective_equipment(
    Image={
        'Bytes': image_encoder(snapshot_url)
    },
    SummarizationAttributes={
        'MinConfidence': 80,
        'RequiredEquipmentTypes': ppe_requirement
    }
)

# json_object = json.dumps(response, indent=4)
# print(json_object)

# Image analysis
person_count = str(len(response["Persons"]))
# print(person_count)
missing_ppe_msg = ""
person_num = 1

# Only proceed if there's a PPE violation
if response["Summary"]["PersonsWithoutRequiredEquipment"] != []:

    # replace ppe requirement value
    # for i in range(len(ppe_requirement)):
    #     if ppe_requirement[i] == "FACE_COVER":
    #         ppe_requirement[i] = "FACE"
    #     if ppe_requirement[i] == "HEAD_COVER":
    #         ppe_requirement[i] = "HEAD"
    #     if ppe_requirement[i] == "HAND_COVER":
    #         ppe_requirement[i] = "RIGHT HAND"
    #         ppe_requirement.append("LEFT HAND")
    # print(ppe_requirement)

    for person in response["Persons"]:
        missing_ppe_msg += "[Person #" + str(person_num) + ":"

        # for bodypart in person["BodyParts"]:
        #     for req in ppe_requirement:
        #         if bodypart["Name"] == req:
        #             if len(bodypart["EquipmentDetections"]) > 0:
        #                 if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
        #                     missing_ppe_msg += "(" + req + "-Uncovered)"
        #             else:
        #                 missing_ppe_msg += "(" + req + ")"

        for bodypart in person["BodyParts"]:
            if bodypart["Name"] == "FACE":
                if len(bodypart["EquipmentDetections"]) > 0:
                    if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                        missing_ppe_msg += "(Face-Uncovered)"
                else:
                    missing_ppe_msg += "(Face)"
            if bodypart["Name"] == "LEFT_HAND":
                if len(bodypart["EquipmentDetections"]) > 0:
                    if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                        missing_ppe_msg += "(Left Hand-Uncovered)"
                else:
                    missing_ppe_msg += "(Left Hand)"
            if bodypart["Name"] == "RIGHT_HAND":
                if len(bodypart["EquipmentDetections"]) > 0:
                    if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                        missing_ppe_msg += "(Right Hand-Uncovered)"
                else:
                    missing_ppe_msg += "(Right Hand)"
            if bodypart["Name"] == "HEAD":
                if len(bodypart["EquipmentDetections"]) > 0:
                    if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                        missing_ppe_msg += "(Head-Uncovered)"
                else:
                    missing_ppe_msg += "(Head)"

        missing_ppe_msg += "]"
        person_num += 1

print(missing_ppe_msg)

# mock data
mv_loc = "Warehouse / MV12"
detected_name = "Bob"
event_time = "19-Aug-2021 (10:10)"

# postCard_ppeViolation(mv_loc, snapshot_url, person_count,
#                       detected_name, missing_ppe_msg, event_time)
