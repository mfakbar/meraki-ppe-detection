import boto3
import json
import time
from urllib.request import urlopen
import requests
import os
from dotenv import load_dotenv
from webex import *


# AWS
load_dotenv()
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')


# snapshot_url = event['image_url']
snapshot_url = "https://thumbs.dreamstime.com/b/seaman-ab-bosun-deck-vessel-ship-wearing-ppe-personal-protective-equipment-helmet-coverall-lifejacket-goggles-safety-141609777.jpg"
# snapshot_url = "https://raw.githubusercontent.com/mfakbar/meraki-ppe-detection/main/IMAGES/seaman_test.jpg"
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

# Image analysis
person_count = str(len(response["Persons"]))
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
        missing_ppe_msg += "[Person #" + str(person_num) + ": "

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

        missing_ppe_msg += "] "
        person_num += 1

print(missing_ppe_msg)


def upload_to_s3(snapshot_url):
    temp_image = requests.get(snapshot_url, stream=True)

    session = boto3.Session()
    s3 = session.resource('s3')

    bucket_name = 'faceforppedetection'
    saved_img = 'snapshot.jpg'

    bucket = s3.Bucket(bucket_name)
    bucket.upload_fileobj(temp_image.raw, saved_img)

    print("Image uploaded to S3")

    return saved_img


def search_face(img):
    bucket = 'faceforppedetection'
    collectionId = 'face_collection_for_PPE_detection'
    fileName = img
    threshold = 70
    maxFaces = 2

    client = boto3.client('rekognition')

    response = client.search_faces_by_image(CollectionId=collectionId,
                                            Image={'S3Object': {
                                                'Bucket': bucket, 'Name': fileName}},
                                            FaceMatchThreshold=threshold,
                                            MaxFaces=maxFaces)

    faceMatches = response['FaceMatches']
    print('Matching faces')
    for match in faceMatches:
        print('FaceId:' + match['Face']['FaceId'])
        print('Employee alias:' + match['Face']['ExternalImageId'])
        print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")

    return faceMatches


saved_img = upload_to_s3(snapshot_url)
face_matches = search_face(saved_img)
detected_face_msg = ""
person_num = 1

for match in face_matches:
    detected_face_msg += "[Person #" + str(person_num) + ": "

    detected_face_msg += match['Face']['ExternalImageId'][:-4] + \
        " ({:.2f}".format(match['Similarity']) + "%)"

    detected_face_msg += "] "
    person_num += 1

print(detected_face_msg)

# mock data
mv_loc = "Warehouse / MV12"
event_time = "19-Aug-2021 / 10:10"

# postCard_ppeViolation(mv_loc, snapshot_url, person_count,
#                       detected_face_msg, missing_ppe_msg, event_time)
