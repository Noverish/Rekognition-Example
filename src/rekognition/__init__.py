from botocore.exceptions import ClientError


def collection_exists(client, collection_id):
    try:
        client.describe_collection(
            CollectionId=collection_id
        )
        return True
    except ClientError:
        return False


def create_collection(client, collection_id):
    client.create_collection(
        CollectionId=collection_id
    )


def upload_face(client, collection_id, bucket_name, key):
    face_name = key.split(".")[0]

    client.index_faces(
        CollectionId=collection_id,
        Image={'S3Object': {'Bucket': bucket_name, 'Name': key}},
        ExternalImageId=face_name,
        DetectionAttributes=['DEFAULT'],
        MaxFaces=1
    )



