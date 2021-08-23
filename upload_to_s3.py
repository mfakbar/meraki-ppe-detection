import requests
import boto3

url = "https://thumbs.dreamstime.com/b/seaman-ab-bosun-deck-vessel-ship-wearing-ppe-personal-protective-equipment-helmet-coverall-lifejacket-goggles-safety-141609777.jpg"
temp_image = requests.get(url, stream=True)

session = boto3.Session()
s3 = session.resource('s3')

bucket_name = 'faceforppedetection'
key = 'seaman_snapshot.jpg'  # key is the name of file on your bucket

bucket = s3.Bucket(bucket_name)
bucket.upload_fileobj(temp_image.raw, key)

print("Image uploaded to S3")
