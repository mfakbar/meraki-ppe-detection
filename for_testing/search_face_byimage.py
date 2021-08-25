import boto3

if __name__ == "__main__":

    bucket = 'faceforppedetection'
    collectionId = 'face_collection_for_PPE_detection'
    fileName = 'seaman_snapshot.jpg'
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
        print
