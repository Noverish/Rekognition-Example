from io import BytesIO
from botocore.exceptions import ClientError


def recognize_face(client, collection_id, image):
    results = []

    faces = _detect(client, image)
    for face in faces:
        cropped = _crop(image, face)
        result = _search(client, collection_id, cropped)

        if result is not None:
            result.update(face)
            results.append(result)

    return results


def _detect(client, image):
    img_width, img_height = image.size

    byte_arr = BytesIO()
    image.save(byte_arr, format='JPEG')
    byte_arr = byte_arr.getvalue()

    response = client.detect_faces(
        Image={
            'Bytes': byte_arr
        },
        Attributes=['DEFAULT']
    )

    faces = []
    for face in response['FaceDetails']:
        box = face['BoundingBox']

        left = int(img_width * box['Left'])
        width = int(img_width * box['Width'])
        top = int(img_height * box['Top'])
        height = int(img_height * box['Height'])

        faces.append({
            'left': left,
            'top': top,
            'width': width,
            'height': height
        })

    return faces


def _crop(image, rect):
    img = image.copy()
    rect = (rect['left'], rect['top'], rect['left'] + rect['width'], rect['top'] + rect['height'])
    return img.crop(rect)


def _search(client, collection_id, image):
    byte_arr = BytesIO()
    image.save(byte_arr, format='JPEG')
    byte_arr = byte_arr.getvalue()

    try:
        response = client.search_faces_by_image(
            CollectionId=collection_id,
            Image={
                'Bytes': byte_arr
            },
            MaxFaces=1
        )
    except ClientError:
        return None

    matches = response['FaceMatches']

    if len(matches) != 0:
        return {
            'name': matches[0]['Face']['ExternalImageId'],
            'similarity': matches[0]['Similarity']
        }
    else:
        return {
            'name': None,
            'similarity': None
        }
