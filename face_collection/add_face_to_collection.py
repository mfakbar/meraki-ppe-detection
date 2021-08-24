import boto3


def add_faces_to_collection(bucket, photo, collection_id):

    client = boto3.client('rekognition')

    response = client.index_faces(CollectionId=collection_id,
                                  Image={'S3Object': {
                                      'Bucket': bucket, 'Name': photo}},
                                  ExternalImageId=photo,
                                  MaxFaces=1,
                                  QualityFilter="AUTO",
                                  DetectionAttributes=['ALL'])

    print('Results for ' + photo)
    print('Faces indexed:')
    for faceRecord in response['FaceRecords']:
        print('  Face ID: ' + faceRecord['Face']['FaceId'])
        print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(
            unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return len(response['FaceRecords'])


def list_s3_file(bucket_name):

    client = boto3.client('s3')

    response = client.list_objects(Bucket=bucket_name)

    key_list = []

    for i in range(len(response["Contents"])):
        key = response["Contents"][i]["Key"]
        key_list.append(key)

    return key_list


def main():
    bucket = "faceforppedetection"
    collection_id = "face_collection_for_PPE_detection"

    key_list = list_s3_file(bucket)

    for key in key_list:
        indexed_faces_count = add_faces_to_collection(
            bucket, key, collection_id)
        print("Faces indexed count: " + str(indexed_faces_count))


if __name__ == "__main__":
    main()
