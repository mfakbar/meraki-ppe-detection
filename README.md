# Meraki PPE and Facial Detection for Workplace Safety

This project detects the event of PPE (personal protective equipment) policy violation, identify the person whose violating the policy, and send a notification to the person directly and also to a dedicated Webex space. The objective is to improve workplace safety and minimize near-miss/hazardous situations that potentially caused by PPE policy violation. The policy violation event is stored in the database to enable the customer to create actionable insights, thus to further improve the workplace safety.


---

The following diagram describes the use case overview.

![Meraki PPE and Facial Detection for Workplace Safety Overview](./IMAGES/Meraki_PPE_and_Facial_Detection_Overview.jpg)

The following diagram describes the PoV high level design.

![Meraki PPE and Facial Detection for Workplace Safety High Level Design](./IMAGES/Meraki_PPE_and_Facial_Detection_HLD.jpg)



## Contacts
* Hung Le (hungl2@cisco.com)
* Muhammad Akbar (muakbar@cisco.com)
* Swati Singh (swsingh3@cisco.com)



## Solution Components
* Camera: Meraki MV
* MQTT broker: Mosquitto
* Database system: MongoDB Atlas
* Recognition engine: AWS Lambda, Rekognition
* Messaging: Webex



## Workflow
![Workflow Diagram](./IMAGES/Meraki_PPE_and_Facial_Detection_LLD.jpg)



# Getting Started
1. Clone the repository.
2. Setup and install all the requirements - optionally, use venv to isolate the project.
```
python -m venv myvenv
python -m pip install -r requirements.txt
```

## Setting up MQTT broker
What we need:
1. A MQTT broker reachable by the MV camera. The MQTT broker needs to be configured on the MV dashboard, following the steps of this [MV Sense guide](https://developer.cisco.com/meraki/mv-sense/#!mqtt/configuring-mqtt-in-the-). For our use case, we use a publicly available MQTT broker ([Mosquitto](test.mosquitto.org)). Customer can deploy their own brokers for guaranteed service.
2. Access to at least one Meraki MV camera with MV Sense license and API key. Also a list of MV serial numbers if our solution is to be deployed on multiple cameras on your the environment.
   
Usage:
1. Input Meraki and MQTT credentials on the [snapshot_and_trigger.py](./snapshot_and_trigger.py) file. These include the MV API key, the cameras serial numbers, the MQTT server and port.

## Setting up face collection
1. [Set up AWS CLI and SDKs](https://docs.aws.amazon.com/rekognition/latest/dg/setup-awscli-sdk.html) and save the `Access` and `Secret` key - This will be used in Lambda deployment.
2. Set up an AWS S3 bucket - In this case the bucket name is `faceforppedetection`.
3. Make the bucket accessible to public. In the bucket permission setting, unblock public access, allow `list` and `read` permission for public access ACL - This is for accessing the snapshot taken from Meraki. In production, it is highly recommended to use separate bucket for storing face collection (private access) and snapshot file (public read access).
4. Upload to the bucket the face images (jpg) we want to use as reference for the recognition engine. The name of the image file is the identity of the person - In this case the file name is the employee/email alias so we can easily send the notification directly to that employee Webex account.
5. Create collection using [create_collection.py](./face_collection/create_collection.py). Choose the name for `collection_id` -  In this case the `collection_id` name is `face_collection_for_PPE_detection` ([AWS reference - Create a face collection](https://docs.aws.amazon.com/rekognition/latest/dg/create-collection-procedure.html)).
6. Add the face images in our S3 bucket to the collection using [add_face_to_collection.py](./face_collection/add_face_to_collection.py) ([AWS reference - Adding face to a collection](https://docs.aws.amazon.com/rekognition/latest/dg/add-faces-to-collection-procedure.html)).

## Setting up database
1. Create MongoDB Atlas collection - In this case the cluster name is `Tables`, and table collection name is `Events`.
2. Define these column in the table: Time, Camera SN, Camera Location, People Count, Names, Missing PPEs.
3. [Create connection](https://docs.atlas.mongodb.com/tutorial/connect-to-your-cluster/) to the cluster, and save the connection string: `mongodb+srv://youraccount:xxxx@cluster0.xxxx.mongodb.net/xxxx`. This will be used to store the event to the database - See Lambda deployment.

## Setting up Webex
1. [Create Webex bot](https://developer.webex.com/docs/bots) and save the `Access Token`.
2. Create a Webex space to send out the notification to, and add the newly created Webex bot to the space.
3. [Get the Webex room ID](https://developer.webex.com/docs/api/v1/rooms/list-rooms) of the newly created space.
4. Webex `Access Token` and `roomId` will be used in Lambda deployment.

## Lambda deployment
1. Change AWS, MongoDB, email domain, and Webex credentials in [ppe_detection_lambda.py](./lambda/ppe_detection_lambda.py) and [webex_lambda.py](./lambda/webex_lambda.py).
2. Add [ppe_detection_lambda.py](./lambda/ppe_detection_lambda.py) and [webex_lambda.py](./lambda/webex_lambda.py) to the `deployment-package.zip` file ([AWS reference - Deploying lambda package using venv .zip file](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)).
3. Create a Lambda function in AWS and upload the `deployment-package.zip` file.
4. In Lambda Runtime Setting, set the Handler to `ppe_detection_lambda.lambda_handler`.
5. In Layers setting, add `arn:aws:lambda:ap-southeast-1:770693421928:layer:Klayers-python38-Pillow:12` as a new layer. This is to add the PIL library to Lambda.
6. In Configuration setting > Triggers > Add API Gateway as a trigger > Set up a REST or HTTP API in API Gateway ([AWS reference - Using Lambda with API GW](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)).
   1. After setting up the API GW, input the endpoint address to the `AWS_API_URL` variable in [snapshot_and_trigger.py](./snapshot_and_trigger.py).


# Sample notification
- Notification to the employee personal Webex account
  ![To personal account](./IMAGES/notification-to-person-sample.png)
- Notification to the Webex space - Note that bounding box will be drawn on every detected PPE and face.
  - Not wearing face and head cover
  ![To space sample 3](./IMAGES/notification-to-space-sample3.png)
  - Not wearing face and head cover, and gloves is missing on the left hand
  ![To space sample 2](./IMAGES/notification-to-space-sample2.png)
  - Not wearing head cover, and the face cover is not fully covering the nose
  ![To space sample 1](./IMAGES/notification-to-space-sample1.png)