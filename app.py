import boto3
import json
import time
from urllib.request import urlopen
import requests
import os
from dotenv import load_dotenv

# AWS access key and secret key
load_dotenv()
a_key = os.getenv('AWS_ACCESS_KEY')
s_key = os.getenv('AWS_SECRET_KEY')

# WEBEX
access_token = "YzYxZjg2N2UtNTZmNi00YzhkLTgzOWUtZmRjZGQ1YWUxN2M3NmIwOGZiODAtZGZh_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
teams_room = "Y2lzY29zcGFyazovL3VzL1JPT00vNTVlODM2MjAtMDBjZC0xMWVjLWE5NGEtOTE0MWYxY2FlM2M5"

# MERAKI
api_key = 'b7f21d401cfcce7311c94edc2a41cd048bea032d'
MV_Camera_SN = "Q2GV-9GBH-4PC3"
base_url = f"https://api.meraki.com/api/v1/devices/{MV_Camera_SN}/camera/generateSnapshot"


# The goal is to get the screenshot and store it in s3 and then use it from there to process it for PPE Detection


def detect_labels(photo, bucket):
    rekog = boto3.client(
        'rekognition', aws_access_key_id=a_key, aws_secret_access_key=s_key)

    # client=boto3.client('rekognition')

    response = rekog.detect_protective_equipment(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                                 SummarizationAttributes={'MinConfidence': 80, 'RequiredEquipmentTypes': ['FACE_COVER', 'HAND_COVER', 'HEAD_COVER']})

    print('Detected PPE for people in image ' + photo)
    print('\nDetected people\n---------------')
    for person in response['Persons']:

        print('Person ID: ' + str(person['Id']))
        print('Body Parts\n----------')
        body_parts = person['BodyParts']
        if len(body_parts) == 0:
            print('No body parts found')
        else:
            for body_part in body_parts:
                print(
                    '\t' + body_part['Name'] + '\n\t\tConfidence: ' + str(body_part['Confidence']))
                print('\n\t\tDetected PPE\n\t\t------------')
                ppe_items = body_part['EquipmentDetections']
                if len(ppe_items) == 0:
                    print('\t\tNo PPE detected on ' + body_part['Name'])
                else:
                    for ppe_item in ppe_items:
                        print(
                            '\t\t' + ppe_item['Type'] + '\n\t\t\tConfidence: ' + str(ppe_item['Confidence']))
                        print('\t\tCovers body part: ' + str(ppe_item['CoversBodyPart']['Value']) + '\n\t\t\tConfidence: ' + str(
                            ppe_item['CoversBodyPart']['Confidence']))
                        print('\t\tBounding Box:')
                        print('\t\t\tTop: ' +
                              str(ppe_item['BoundingBox']['Top']))
                        print('\t\t\tLeft: ' +
                              str(ppe_item['BoundingBox']['Left']))
                        print('\t\t\tWidth: ' +
                              str(ppe_item['BoundingBox']['Width']))
                        print('\t\t\tHeight: ' +
                              str(ppe_item['BoundingBox']['Height']))
                        print('\t\t\tConfidence: ' +
                              str(ppe_item['Confidence']))
            print()
        print()

    print('Person ID Summary\n----------------')
    display_summary('With required equipment',
                    response['Summary']['PersonsWithRequiredEquipment'])
    display_summary('Without required equipment',
                    response['Summary']['PersonsWithoutRequiredEquipment'])
    display_summary('Indeterminate',
                    response['Summary']['PersonsIndeterminate'])

    print()
    return len(response['Persons'])

# Display summary information for supplied summary.


def display_summary(summary_type, summary):
    print(summary_type + '\n\tIDs: ', end='')
    if (len(summary) == 0):
        print('None')
    else:
        for num, id in enumerate(summary, start=0):
            if num == len(summary)-1:
                print(id)
            else:
                print(str(id) + ', ', end='')


def main():
    photo = 'snapshot.jpg'  # The name of the image you uploaded in the bucket
    bucket = 'faceforppedetection'  # Enter the name of the bucket here
    person_count = detect_labels(photo, bucket)
    print("Persons detected: " + str(person_count))


if __name__ == "__main__":
    main()
