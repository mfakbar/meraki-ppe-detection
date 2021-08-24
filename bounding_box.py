import boto3
import io
from PIL import Image, ImageDraw


bounding_box = [
    {
        'Width': 0.17668716609477997,
        'Height': 0.16557781398296356,
        'Left': 0.5176424980163574,
        'Top': 0.6662641167640686
    },
    {
        'Width': 0.2005884349346161,
        'Height': 0.1571822315454483,
        'Left': 0.5232090353965759,
        'Top': 0.0009936005808413029
    }
]


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

        print('Left: ' + '{0:.0f}'.format(left))
        print('Top: ' + '{0:.0f}'.format(top))
        print('Width: ' + "{0:.0f}".format(width))
        print('Height: ' + "{0:.0f}".format(height))

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
                      ExtraArgs={'ACL': 'public-read'})

    print("Image with boxes uploaded to S3")


def main():
    bucket_name = "faceforppedetection"
    photo = "snapshot.jpg"
    key_name = "snapshot_with_boxes.jpg"

    draw_boxes(photo, bucket_name, bounding_box, key_name)


if __name__ == "__main__":
    main()
