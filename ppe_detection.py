import boto3
import json
import time
import requests
import os
from dotenv import load_dotenv
from webex import *
import io
from PIL import Image, ImageDraw

# AWS access key and secret key
load_dotenv()
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')

# Mock PPE policy from DB
ppe_requirement = ['FACE_COVER', 'HAND_COVER', 'HEAD_COVER']

# Mock data from Meraki
snapshot_url = "https://raw.githubusercontent.com/mfakbar/meraki-ppe-detection/main/face_collection/mock_images/Test3.jpg"
# snapshot_url = "https://www.missiontoseafarers.org/wp-content/uploads/FAC-brochure-cover.jpg"
mv_loc = "Warehouse / MV12"
event_time = "19-Aug-2021 / 10:10"

# Employee email domain
email_domain = "@cisco.com"


def detect_labels(photo, bucket_name):
    # Connect to AWS Rekognition
    rekog = boto3.client('rekognition', region_name='ap-southeast-1',
                         aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    response = rekog.detect_protective_equipment(
        Image={'S3Object': {'Bucket': bucket_name, 'Name': photo}},
        SummarizationAttributes={
            'MinConfidence': 80,
            'RequiredEquipmentTypes': ppe_requirement
        }
    )

    # Image analysis
    person_count = str(len(response["Persons"]))
    missing_ppe_msg = ""
    bounding_box = []
    person_num = 1

    # Only proceed if there's a PPE violation
    if response["Summary"]["PersonsWithoutRequiredEquipment"] != []:

        for person in response["Persons"]:
            missing_ppe_msg += "[Person #" + str(person_num) + ": "

            for bodypart in person["BodyParts"]:
                if bodypart["Name"] == "FACE":
                    if len(bodypart["EquipmentDetections"]) > 0:
                        bounding_box.append(
                            bodypart["EquipmentDetections"][0]["BoundingBox"])
                        if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                            missing_ppe_msg += "(Face-Uncovered)"
                    else:
                        missing_ppe_msg += "(Face)"
                if bodypart["Name"] == "LEFT_HAND":
                    if len(bodypart["EquipmentDetections"]) > 0:
                        bounding_box.append(
                            bodypart["EquipmentDetections"][0]["BoundingBox"])
                        if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                            missing_ppe_msg += "(Left Hand-Uncovered)"
                    else:
                        missing_ppe_msg += "(Left Hand)"
                if bodypart["Name"] == "RIGHT_HAND":
                    if len(bodypart["EquipmentDetections"]) > 0:
                        bounding_box.append(
                            bodypart["EquipmentDetections"][0]["BoundingBox"])
                        if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                            missing_ppe_msg += "(Right Hand-Uncovered)"
                    else:
                        missing_ppe_msg += "(Right Hand)"
                if bodypart["Name"] == "HEAD":
                    if len(bodypart["EquipmentDetections"]) > 0:
                        bounding_box.append(
                            bodypart["EquipmentDetections"][0]["BoundingBox"])
                        if bodypart["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False:
                            missing_ppe_msg += "(Head-Uncovered)"
                    else:
                        missing_ppe_msg += "(Head)"

            missing_ppe_msg += "] "
            person_num += 1

    print("Person count: ", person_count)
    print("Missing ppe msg: ", missing_ppe_msg)

    return missing_ppe_msg, person_count, bounding_box


def upload_to_s3(snapshot_url, bucket_name, key_name):
    temp_image = requests.get(snapshot_url, stream=True)

    session = boto3.Session()
    s3 = session.resource('s3')

    bucket = s3.Bucket(bucket_name)
    bucket.upload_fileobj(temp_image.raw, key_name)

    print("Image uploaded to S3")

    return key_name


def search_face(photo, bucket_name, collection_name):

    threshold = 70
    maxFaces = 2

    rekog = boto3.client('rekognition')

    response = rekog.search_faces_by_image(CollectionId=collection_name,
                                           Image={'S3Object': {
                                               'Bucket': bucket_name, 'Name': photo}},
                                           FaceMatchThreshold=threshold,
                                           MaxFaces=maxFaces)

    faceMatches = response['FaceMatches']

    print('Matching faces:')
    for match in faceMatches:
        print('Employee alias:' + match['Face']['ExternalImageId'])
        print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")

    detected_face_msg = ""
    bounding_box = [response['SearchedFaceBoundingBox']]
    detected_names = []
    person_num = 1

    for match in faceMatches:
        detected_names.append(match['Face']['ExternalImageId'][:-4])

        detected_face_msg += "[Person #" + str(person_num) + ": "

        detected_face_msg += match['Face']['ExternalImageId'][:-4] + \
            " ({:.2f}".format(match['Similarity']) + "%)"

        detected_face_msg += "] "
        person_num += 1

    if len(faceMatches) == 0:
        detected_face_msg = "Face ID not recognized"

    print("Detected face msg: ", detected_face_msg)

    return detected_face_msg, bounding_box, detected_names


# Draw bounding box to the image
def draw_boxes(photo, bucket_name, bounding_box, key_name):

    # Load image from S3 bucket
    session = boto3.Session()
    s3 = session.resource('s3')
    s3_object = s3.Object(bucket_name, photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # Calculate and display bounding boxes for each detected ppe
    for per_ppe_box in bounding_box:

        left = imgWidth * per_ppe_box['Left']
        top = imgHeight * per_ppe_box['Top']
        width = imgWidth * per_ppe_box['Width']
        height = imgHeight * per_ppe_box['Height']

        points = (
            (left, top),
            (left + width, top),
            (left + width, top + height),
            (left, top + height),
            (left, top)

        )

        # Draw rectangle
        draw.rectangle([left, top, left + width, top + height],
                       outline='#00d400')

    # image.show()

    # Upload image with boxes
    in_mem_file = io.BytesIO()  # Save the image to an in-memory file
    image.save(in_mem_file, format=image.format)
    in_mem_file.seek(0)

    # Upload image to s3
    s3 = boto3.client('s3')
    s3.upload_fileobj(in_mem_file, bucket_name, key_name,
                      ExtraArgs={
                          'ACL': 'public-read',
                          'ContentType': 'image/jpeg',
                          'ContentDisposition': 'inline; filename='+key_name,
                      }
                      )

    print("Image with boxes uploaded to S3")


def main():
    bucket_name = "faceforppedetection"  # AWS S3 bucket name
    collection_name = "face_collection_for_PPE_detection"  # AWS collection id
    region = "ap-southeast-1"  # AWS region
    key_name = "snapshot.jpg"  # The name of the image file we want to upload to the bucket
    key_name_box = "snapshot_with_boxes.jpeg"  # The name of the image file w/ boxes

    # Upload Meraki snapshot to S3
    photo = upload_to_s3(snapshot_url, bucket_name, key_name)

    # Detect missing ppe and person count
    missing_ppe_msg, person_count, bounding_box = detect_labels(
        photo, bucket_name)

    # Detect face
    detected_face_msg, bounding_box_face, detected_names = search_face(
        photo, bucket_name, collection_name)

    # Append bounding box
    if len(bounding_box_face) > 0:
        for box in bounding_box_face:
            bounding_box.append(box)
    print("Final bounding box: ", bounding_box)
    print

    # Draw bounding box
    draw_boxes(photo, bucket_name, bounding_box, key_name_box)

    # Send notification to employee if any names are detected
    if len(detected_names) > 0:
        for name in detected_names:
            detected_email = name+email_domain
            post_message(mv_loc, detected_email, event_time)

    # Webex notification to security team
    s3_obj_url = "https://" + bucket_name + ".s3." + \
        region + ".amazonaws.com/" + key_name_box
    print(s3_obj_url)

    post_card(mv_loc, s3_obj_url, person_count,
              detected_face_msg, missing_ppe_msg, event_time)


if __name__ == "__main__":
    main()
